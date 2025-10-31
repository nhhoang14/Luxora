"""
Dump selected project models into Django fixture JSON files.

Usage (inside your project's virtualenv):
  python dump_fixtures.py --all
  python dump_fixtures.py --models accounts.User products.Product orders.Order
  python dump_fixtures.py --out ./my_fixtures --models accounts.User

Notes:
- Run with the project's venv python (or activate venv first).
- The script writes to the app's fixtures/ directory when possible.
"""
import os
import sys
import json
import argparse
from decimal import Decimal
from datetime import datetime, date
from pathlib import Path

import django
from django.apps import apps
from django.conf import settings

# --- Bootstrap Django ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "luxora.settings")
django.setup()


def convert_value(v):
    if v is None:
        return None
    if isinstance(v, (int, float, str, bool)):
        return v
    if isinstance(v, Decimal):
        # prefer int when no fractional part
        return int(v) if v % 1 == 0 else float(v)
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    # FileField / ImageField -> store path (string)
    if hasattr(v, "name"):
        return str(v.name)
    # fallback to string
    return str(v)


def model_to_fixture(model, qs=None):
    model_label = f"{model._meta.app_label}.{model._meta.model_name}"
    qs = qs or model.objects.all()
    fixtures = []
    # collect m2m field names
    m2m_field_names = [f.name for f in model._meta.many_to_many]
    # collect local fields to include (exclude AutoField pk handled separately)
    local_fields = [f for f in model._meta.local_fields if not getattr(f, "auto_created", False)]
    for inst in qs:
        pk = getattr(inst, inst._meta.pk.name)
        fields = {}
        for field in local_fields:
            name = field.name
            if field.primary_key:
                continue
            val = getattr(inst, name)
            # for ForeignKey store related pk (or None)
            if field.get_internal_type() == "ForeignKey" or field.many_to_one:
                fields[name] = convert_value(getattr(val, val._meta.pk.name) if val else None)
            else:
                fields[name] = convert_value(val)
        # many-to-many
        for m2m in m2m_field_names:
            try:
                values = list(getattr(inst, m2m).values_list("pk", flat=True))
            except Exception:
                values = []
            fields[m2m] = values
        fixtures.append({"model": model_label, "pk": pk, "fields": fields})
    return fixtures


def write_fixture(app_label, model_name, data, out_dir=None):
    # choose fixtures dir: <app>/fixtures/ if exists, else project_root/fixtures/<app>/
    app_path = Path(app_label)
    if app_path.exists():
        fixtures_dir = app_path / "fixtures"
    else:
        fixtures_dir = (Path(settings.BASE_DIR) / "fixtures" / app_label)
    if out_dir:
        fixtures_dir = Path(out_dir) / app_label
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    file_path = fixtures_dir / f"{model_name}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return file_path


def dump_models(model_labels, out_dir=None):
    total = 0
    for label in model_labels:
        try:
            model = apps.get_model(label)
        except LookupError:
            print(f"✖ Model not found: {label}")
            continue
        print(f"Dumping {label} ...", end=" ")
        try:
            fixtures = model_to_fixture(model)
        except AttributeError as e:
            # Manager not available (e.g. swapped user model or import-time issues)
            print(f"skipped (manager not available): {e}")
            continue
        if not fixtures:
            print("no rows, skipped")
            continue
        path = write_fixture(model._meta.app_label, model._meta.model_name, fixtures, out_dir=out_dir)
        print(f"wrote {len(fixtures)} -> {path}")
        total += len(fixtures)
    print(f"Done. Total rows dumped: {total}")


def get_all_models():
    return [f"{m._meta.app_label}.{m._meta.model_name}" for m in apps.get_models()]


def parse_args():
    p = argparse.ArgumentParser(description="Dump DB models to Django fixture JSON files.")
    p.add_argument("--models", "-m", nargs="+", help="Model labels to dump (app_label.ModelName), e.g. products.Product")
    p.add_argument("--all", action="store_true", help="Dump all installed models")
    p.add_argument("--out", "-o", help="Output base directory for fixtures")
    return p.parse_args()


def main():
    args = parse_args()
    if args.all:
        models = get_all_models()
    elif args.models:
        models = args.models
    else:
        # sensible defaults: use project's AUTH_USER_MODEL if swapped
        user_model_label = getattr(settings, "AUTH_USER_MODEL", "auth.User")
        models = [
            user_model_label,
            "products.category",
            "products.product",
            "core.contactmessage" if apps.is_installed("core") else None,
        ]
        models = [m for m in models if m]
    dump_models(models, out_dir=args.out)


if __name__ == "__main__":
    main()
