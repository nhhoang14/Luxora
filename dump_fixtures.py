import os
import django
import json
from django.apps import apps
from decimal import Decimal
from datetime import datetime
from pathlib import Path

# --- Thiết lập Django ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'luxora.settings')
django.setup()

def serialize_objects_for_fixture(objects, model, model_name):
    fixtures = []
    for obj in objects:
        pk = obj.pop("id", None)
        fields = {}

        # Chuyển đổi giá trị về dạng có thể JSON hóa
        for k, v in obj.items():
            if isinstance(v, Decimal):
                v = int(v) if v % 1 == 0 else float(v)
            elif isinstance(v, datetime):
                v = v.isoformat()
            fields[k] = v

        # Lấy dữ liệu ManyToMany (ví dụ: categories, colors)
        m2m_fields = getattr(model._meta, "many_to_many", [])
        if pk:
            instance = model.objects.get(pk=pk)
            for field in m2m_fields:
                fields[field.name] = list(
                    getattr(instance, field.name).values_list('pk', flat=True)
                )

        fixtures.append({
            "model": model_name,
            "pk": pk,
            "fields": fields
        })

    return fixtures


def dump_model(model_label):
    try:
        model = apps.get_model(model_label)
    except LookupError:
        print(f"Bỏ qua {model_label} (model không tồn tại).")
        return

    app_label = model._meta.app_label
    model_name = model._meta.model_name

    # Tạo thư mục fixtures
    app_path = Path(app_label)
    fixtures_dir = app_path / "fixtures" if app_path.exists() else Path("core") / "fixtures"
    fixtures_dir.mkdir(exist_ok=True, parents=True)

    file_path = fixtures_dir / f"{model_name}s.json"

    objects = list(model.objects.all().values())
    if not objects:
        print(f"⏭️  {model_label} không có dữ liệu, bỏ qua.")
        return

    serialized = serialize_objects_for_fixture(objects, model, f"{app_label}.{model_name}")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(serialized, f, ensure_ascii=False, indent=2)

    print(f"Đã dump {len(objects)} bản ghi của {model_label} → {file_path}")


# --- Danh sách model muốn dump ---
MODELS_TO_DUMP = [
    "auth.User",
    "products.Color", 
    "products.Category",
    "products.Product",
    "core.ContactMessage",
]

def main():
    print("Bắt đầu dump fixtures...\n")
    for model_label in MODELS_TO_DUMP:
        try:
            dump_model(model_label)
        except Exception as e:
            print(f"Lỗi khi dump {model_label}: {e}")
    print("\nHoàn tất dump fixtures!")

if __name__ == "__main__":
    main()
