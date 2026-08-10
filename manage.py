#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys
from pathlib import Path


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(base_dir))

    from dotenv import load_dotenv

    # Cargar .env antes del setdefault para respetar DJANGO_SETTINGS_MODULE en prod.
    load_dotenv(base_dir / ".env")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Is it installed and available on your PYTHONPATH?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
