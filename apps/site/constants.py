"""Mapeo newsletter → Mailchimp (Audience Petralicious, group Idioma / Jazyk)."""

NEWSLETTER_LANGUAGES = {
    "es": {
        "interest_name": "Español",
        "default_tag": "WEB_ES",
        "settings_interest_field": "mailchimp_interest_es_id",
        "settings_tag_field": "mailchimp_web_tag_es",
    },
    "sk": {
        "interest_name": "Slovenčina",
        "default_tag": "WEB_SK",
        "settings_interest_field": "mailchimp_interest_sk_id",
        "settings_tag_field": "mailchimp_web_tag_sk",
    },
}

LANGUAGE_CATEGORY_NAME = "Idioma / Jazyk"
DEFAULT_AUDIENCE_NAME = "Petralicious"
TAG_PATTERN = r"^[A-Z][A-Z0-9_]{0,39}$"
MAX_EXTRA_TAGS = 10
