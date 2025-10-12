import os
import django
import json
from decimal import Decimal
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'luxora.settings')
django.setup()

from core.models import Category, Product

def serialize_objects(objects):
    result = []
    for obj in objects:
        new_obj = {}
        for k, v in obj.items():
            if isinstance(v, Decimal):
                if v % 1 == 0:
                    new_obj[k] = int(v)
                else:
                    new_obj[k] = float(v)
            elif isinstance(v, datetime):
                new_obj[k] = v.isoformat()
            else:
                new_obj[k] = v
        result.append(new_obj)
    return result

fixtures = {
    'categories': Category,
    'products': Product,
}

for name, model in fixtures.items():
    objects = model.objects.all().values()
    objects_serialized = serialize_objects(objects)
    path = f'core/fixtures/{name}.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(objects_serialized, f, ensure_ascii=False, indent=2)
    print(f"Dumped {name}.json successfully")
