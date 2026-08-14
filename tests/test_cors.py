import re

import pytest

from config.settings.cors_defaults import PRODUCTION_CORS_ORIGIN_REGEXES


def _matches(origin: str) -> bool:
    return any(re.fullmatch(pattern, origin) for pattern in PRODUCTION_CORS_ORIGIN_REGEXES)


@pytest.mark.parametrize(
    "origin",
    [
        "https://petralicious-aac3c.web.app",
        "https://preview-channel.web.app",
        "https://petralicious.com",
        "https://www.petralicious.com",
        "https://admin.petralicious.com",
        "https://petralicious.sk",
        "https://www.petralicious.sk",
        "https://app.petralicious.sk",
    ],
)
def test_production_cors_allows_petralicious_and_webapp(origin):
    assert _matches(origin)


@pytest.mark.parametrize(
    "origin",
    [
        "http://petralicious.sk",
        "https://evil.com",
        "https://web.app",
        "https://petralicious.sk.evil.com",
        "https://notpetralicious.sk",
        "https://foo.bar.petralicious.sk",
    ],
)
def test_production_cors_rejects_other_origins(origin):
    assert not _matches(origin)
