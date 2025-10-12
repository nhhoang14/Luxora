import os
import django
import json
from decimal import Decimal
from datetime import datetime
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'luxora.settings')
django.setup()

from core.models import Category, Product

def serialize_objects_for_fixture(objects, model_name):
    fixtures = []
    for obj in objects:
        fields = {}
        pk = obj.get('id')
        for k, v in obj.items():
            if k == 'id':
                continue
            if isinstance(v, Decimal):
                if v % 1 == 0:
                    fields[k] = int(v)
                else:
                    fields[k] = float(v)
            elif isinstance(v, datetime):
                fields[k] = v.isoformat()
            else:
                fields[k] = v
        fixtures.append({
            "model": model_name,
            "pk": pk,
            "fields": fields
        })
    return fixtures

# Map model -> Django app label + model
fixtures_map = {
    'categories': ('core.category', Category),
    'products': ('core.product', Product),
}

# Tạo thư mục fixtures nếu chưa tồn tại
Path("core/fixtures").mkdir(exist_ok=True)

for name, (model_name, model) in fixtures_map.items():
    objects = model.objects.all().values()
    serialized = serialize_objects_for_fixture(objects, model_name)
    path = f'core/fixtures/{name}.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(serialized, f, ensure_ascii=False, indent=2)
    print(f"Dumped {name}.json successfully")
