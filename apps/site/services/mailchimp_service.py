from __future__ import annotations

import hashlib
import logging
import re
from typing import Any

import requests
from django.conf import settings as django_settings
from django.utils import timezone

from apps.common.exceptions import BusinessError
from apps.site.constants import (
    DEFAULT_AUDIENCE_NAME,
    LANGUAGE_CATEGORY_NAME,
    NEWSLETTER_LANGUAGES,
)
from apps.site.models import NewsletterSubscriber, SiteSettings
from apps.site.selectors import get_site_settings

logger = logging.getLogger(__name__)

MAILCHIMP_TIMEOUT = 15
TAG_RE = re.compile(r"^[A-Z][A-Z0-9_]{0,39}$")


def subscriber_hash(email: str) -> str:
    return hashlib.md5(
        email.strip().lower().encode("utf-8"),
        usedforsecurity=False,
    ).hexdigest()


def normalize_extra_tags(tags: list[str] | None) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for raw in tags or []:
        tag = (raw or "").strip().upper()
        if not tag:
            continue
        if not TAG_RE.match(tag):
            raise BusinessError(
                "NEWSLETTER_TAG_INVALID",
                "Cada tag debe ser A-Z, números o guión bajo (ej. FREEBIE_ES, WAITLIST).",
                http_status=422,
            )
        if tag in seen:
            continue
        seen.add(tag)
        cleaned.append(tag)
    return cleaned


def language_web_tag(*, language: str, site: SiteSettings) -> str:
    spec = NEWSLETTER_LANGUAGES[language]
    stored = (getattr(site, spec["settings_tag_field"]) or "").strip().upper()
    return stored or spec["default_tag"]


def language_group_label(language: str) -> str:
    return NEWSLETTER_LANGUAGES[language]["interest_name"]


def datacenter_from_api_key(api_key: str) -> str:
    raw = (api_key or "").strip()
    if "-" not in raw:
        raise BusinessError(
            "MAILCHIMP_API_KEY_INVALID",
            "La API key de Mailchimp debe terminar en el datacenter (ej. …-us21).",
            http_status=422,
        )
    dc = raw.rsplit("-", 1)[-1].strip().lower()
    if not re.match(r"^[a-z]{2,4}\d+$", dc):
        raise BusinessError(
            "MAILCHIMP_API_KEY_INVALID",
            "No se pudo leer el datacenter de la API key (sufijo tipo us21).",
            http_status=422,
        )
    return dc


def marketing_configured(site: SiteSettings | None = None) -> bool:
    site = site or get_site_settings()
    return bool(
        site.mailchimp_enabled
        and (site.mailchimp_api_key or "").strip()
        and (site.mailchimp_audience_id or "").strip()
    )


def transactional_configured(site: SiteSettings | None = None) -> bool:
    site = site or get_site_settings()
    return bool((site.mailchimp_transactional_api_key or "").strip())


def _marketing_request(
    site: SiteSettings,
    method: str,
    path: str,
    *,
    json: dict | None = None,
    params: dict | None = None,
) -> dict:
    api_key = (site.mailchimp_api_key or "").strip()
    dc = datacenter_from_api_key(api_key)
    url = f"https://{dc}.api.mailchimp.com/3.0{path}"
    response = requests.request(
        method,
        url,
        auth=("anystring", api_key),
        json=json,
        params=params,
        timeout=MAILCHIMP_TIMEOUT,
        headers={"User-Agent": "Recetario-Backend"},
    )
    if response.status_code >= 400:
        detail = _mailchimp_error_message(response)
        raise BusinessError(
            "MAILCHIMP_API_ERROR",
            detail,
            http_status=422,
            details={"status": response.status_code},
        )
    if response.status_code == 204 or not response.content:
        return {}
    payload = response.json()
    return payload if isinstance(payload, dict) else {"data": payload}


def _mailchimp_error_message(response: requests.Response) -> str:
    try:
        body = response.json()
    except ValueError:
        return (response.text or f"Mailchimp HTTP {response.status_code}")[:500]
    detail = body.get("detail") or body.get("title") or str(body)
    errors = body.get("errors") or []
    if errors:
        extra = "; ".join(
            f"{item.get('field', '')}: {item.get('message', item)}" for item in errors[:5]
        )
        detail = f"{detail} ({extra})"
    return str(detail)[:500]


def list_interest_categories(*, site: SiteSettings | None = None) -> list[dict]:
    site = site or get_site_settings()
    if not marketing_configured(site):
        raise BusinessError(
            "MAILCHIMP_NOT_CONFIGURED",
            "Configura API key y Audience ID de Mailchimp antes de listar grupos.",
            http_status=422,
        )
    audience_id = site.mailchimp_audience_id.strip()
    categories_payload = _marketing_request(
        site,
        "GET",
        f"/lists/{audience_id}/interest-categories",
        params={"count": 100},
    )
    result = []
    for category in categories_payload.get("categories") or []:
        category_id = category.get("id")
        interests_payload = _marketing_request(
            site,
            "GET",
            f"/lists/{audience_id}/interest-categories/{category_id}/interests",
            params={"count": 100},
        )
        result.append(
            {
                "id": category_id,
                "title": category.get("title"),
                "type": category.get("type"),
                "interests": [
                    {"id": item.get("id"), "name": item.get("name")}
                    for item in interests_payload.get("interests") or []
                ],
            }
        )
    return result


def resolve_language_interests(site: SiteSettings) -> dict[str, str]:
    """language code → interest id. Usa IDs del admin o resuelve por nombre."""
    resolved: dict[str, str] = {}
    for code, spec in NEWSLETTER_LANGUAGES.items():
        stored = (getattr(site, spec["settings_interest_field"]) or "").strip()
        if stored:
            resolved[code] = stored
    missing = [code for code in NEWSLETTER_LANGUAGES if code not in resolved]
    if not missing:
        return resolved

    categories = list_interest_categories(site=site)
    category = _match_language_category(categories, site.mailchimp_language_category_id)
    if category is None:
        raise BusinessError(
            "MAILCHIMP_GROUP_NOT_FOUND",
            f"No se encontró el grupo '{LANGUAGE_CATEGORY_NAME}' en la Audience.",
            http_status=422,
        )
    interests_by_name = {
        (item.get("name") or "").strip().lower(): item.get("id") or ""
        for item in category.get("interests") or []
    }
    for code in missing:
        name = NEWSLETTER_LANGUAGES[code]["interest_name"].lower()
        interest_id = interests_by_name.get(name, "")
        if not interest_id:
            raise BusinessError(
                "MAILCHIMP_INTEREST_NOT_FOUND",
                f"No se encontró el interest '{NEWSLETTER_LANGUAGES[code]['interest_name']}' "
                f"en '{LANGUAGE_CATEGORY_NAME}'.",
                http_status=422,
            )
        resolved[code] = interest_id
    return resolved


def _match_language_category(categories: list[dict], category_id: str) -> dict | None:
    wanted_id = (category_id or "").strip()
    if wanted_id:
        for category in categories:
            if category.get("id") == wanted_id:
                return category
    wanted_title = LANGUAGE_CATEGORY_NAME.strip().lower()
    for category in categories:
        title = (category.get("title") or "").strip().lower()
        if title == wanted_title or "idioma" in title:
            return category
    return categories[0] if len(categories) == 1 else None


def _marketing_permission_payload(site: SiteSettings, *, consent: bool) -> list[dict]:
    ids = [
        item.strip()
        for item in (site.mailchimp_marketing_permission_ids or "").split(",")
        if item.strip()
    ]
    if not ids:
        ids = _discover_marketing_permission_ids(site)
    return [{"marketing_permission_id": pid, "enabled": bool(consent)} for pid in ids]


def _discover_marketing_permission_ids(site: SiteSettings) -> list[str]:
    audience_id = site.mailchimp_audience_id.strip()
    try:
        payload = _marketing_request(
            site,
            "GET",
            f"/lists/{audience_id}/members",
            params={"count": 1, "fields": "members.marketing_permissions"},
        )
    except BusinessError:
        return []
    members = payload.get("members") or []
    if not members:
        return []
    return [
        item.get("marketing_permission_id")
        for item in members[0].get("marketing_permissions") or []
        if item.get("marketing_permission_id")
    ]


def _merge_fields(name: str) -> dict[str, str]:
    parts = (name or "").strip().split(None, 1)
    if not parts:
        return {}
    fields = {"FNAME": parts[0][:100]}
    if len(parts) > 1:
        fields["LNAME"] = parts[1][:100]
    return fields


def upsert_newsletter_member(*, subscriber: NewsletterSubscriber) -> NewsletterSubscriber:
    site = get_site_settings()
    if not marketing_configured(site):
        subscriber.mailchimp_status = NewsletterSubscriber.MailchimpStatus.SKIPPED
        subscriber.mailchimp_error = ""
        subscriber.save(update_fields=["mailchimp_status", "mailchimp_error", "updated_at"])
        return subscriber

    language = (subscriber.language or "").strip().lower()
    if language not in NEWSLETTER_LANGUAGES:
        subscriber.mailchimp_status = NewsletterSubscriber.MailchimpStatus.FAILED
        subscriber.mailchimp_error = "Idioma de suscripción no soportado para Mailchimp."
        subscriber.save(update_fields=["mailchimp_status", "mailchimp_error", "updated_at"])
        return subscriber

    try:
        interest_ids = resolve_language_interests(site)
        web_tag = language_web_tag(language=language, site=site)
        tags = _unique_tags([web_tag, *list(subscriber.extra_tags or [])])
        interests = {interest_id: False for interest_id in interest_ids.values()}
        interests[interest_ids[language]] = True
        status_if_new = "pending" if site.mailchimp_double_opt_in else "subscribed"
        body: dict[str, Any] = {
            "email_address": subscriber.email,
            "status_if_new": status_if_new,
            "merge_fields": _merge_fields(subscriber.name),
            "interests": interests,
        }
        permissions = _marketing_permission_payload(site, consent=subscriber.consent)
        if permissions:
            body["marketing_permissions"] = permissions

        audience_id = site.mailchimp_audience_id.strip()
        member_path = f"/lists/{audience_id}/members/{subscriber_hash(subscriber.email)}"
        _marketing_request(site, "PUT", member_path, json=body)
        _marketing_request(
            site,
            "POST",
            f"{member_path}/tags",
            json={"tags": [{"name": tag, "status": "active"} for tag in tags]},
        )
    except BusinessError as exc:
        logger.warning("Mailchimp sync failed for %s: %s", subscriber.email, exc)
        subscriber.mailchimp_status = NewsletterSubscriber.MailchimpStatus.FAILED
        subscriber.mailchimp_error = str(exc)
        subscriber.save(update_fields=["mailchimp_status", "mailchimp_error", "updated_at"])
        return subscriber
    except requests.RequestException as exc:
        logger.warning("Mailchimp network error for %s: %s", subscriber.email, exc)
        subscriber.mailchimp_status = NewsletterSubscriber.MailchimpStatus.FAILED
        subscriber.mailchimp_error = str(exc)[:500]
        subscriber.save(update_fields=["mailchimp_status", "mailchimp_error", "updated_at"])
        return subscriber

    subscriber.mailchimp_status = NewsletterSubscriber.MailchimpStatus.SYNCED
    subscriber.mailchimp_synced_at = timezone.now()
    subscriber.mailchimp_audience_id = audience_id
    subscriber.mailchimp_audience_name = (
        site.mailchimp_audience_name.strip() or DEFAULT_AUDIENCE_NAME
    )
    subscriber.mailchimp_group = language_group_label(language)
    subscriber.mailchimp_tags = tags
    subscriber.mailchimp_error = ""
    subscriber.save(
        update_fields=[
            "mailchimp_status",
            "mailchimp_synced_at",
            "mailchimp_audience_id",
            "mailchimp_audience_name",
            "mailchimp_group",
            "mailchimp_tags",
            "mailchimp_error",
            "updated_at",
        ]
    )
    return subscriber


def unsubscribe_mailchimp_member(*, subscriber: NewsletterSubscriber) -> None:
    site = get_site_settings()
    if not marketing_configured(site):
        return
    audience_id = (subscriber.mailchimp_audience_id or site.mailchimp_audience_id or "").strip()
    if not audience_id:
        return
    try:
        _marketing_request(
            site,
            "PATCH",
            f"/lists/{audience_id}/members/{subscriber_hash(subscriber.email)}",
            json={"status": "unsubscribed"},
        )
    except BusinessError as exc:
        if exc.details and exc.details.get("status") == 404:
            return
        logger.warning("Mailchimp unsubscribe failed for %s: %s", subscriber.email, exc)


def delete_newsletter_subscriber(*, subscriber: NewsletterSubscriber) -> None:
    unsubscribe_mailchimp_member(subscriber=subscriber)
    subscriber.delete()


def dispatch_mailchimp_sync(*, subscriber_id: str) -> None:
    from apps.site.tasks import sync_newsletter_to_mailchimp_task

    if django_settings.MAIL_ASYNC:
        sync_newsletter_to_mailchimp_task.delay(subscriber_id)
        return
    subscriber = NewsletterSubscriber.objects.filter(pk=subscriber_id).first()
    if subscriber is None:
        return
    upsert_newsletter_member(subscriber=subscriber)


def send_transactional_via_mailchimp(
    *,
    to: str,
    subject: str,
    text: str,
    html: str | None = None,
    from_email: str | None = None,
) -> dict:
    site = get_site_settings()
    api_key = (site.mailchimp_transactional_api_key or "").strip()
    if not api_key:
        raise BusinessError(
            "MAILCHIMP_TRANSACTIONAL_NOT_CONFIGURED",
            "Falta la API key transaccional de Mailchimp (Mandrill).",
            http_status=422,
        )
    sender = (from_email or site.mailchimp_from_email or django_settings.DEFAULT_FROM_EMAIL).strip()
    from_name = (site.mailchimp_from_name or django_settings.SITE_NAME).strip()
    payload = {
        "key": api_key,
        "message": {
            "from_email": sender,
            "from_name": from_name,
            "to": [{"email": to, "type": "to"}],
            "subject": subject,
            "text": text,
            "html": html or text,
        },
    }
    response = requests.post(
        "https://mandrillapp.com/api/1.0/messages/send",
        json=payload,
        timeout=MAILCHIMP_TIMEOUT,
        headers={"User-Agent": "Recetario-Backend"},
    )
    if response.status_code >= 400:
        raise RuntimeError(_mailchimp_error_message(response))
    body = response.json()
    results = body if isinstance(body, list) else [body]
    first = results[0] if results else {}
    status = (first.get("status") or "").lower()
    if status in {"rejected", "invalid"}:
        raise RuntimeError(
            first.get("reject_reason") or first.get("status") or "Mailchimp transactional rejected"
        )
    return {"to": to, "subject": subject, "provider": "mailchimp"}


def _unique_tags(tags: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for tag in tags:
        normalized = (tag or "").strip().upper()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result
