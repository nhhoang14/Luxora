from django.apps import apps

def site_categories(request):
    Category = apps.get_model('products', 'Category')
    return {
        "categories": Category.objects.all().order_by("order") if hasattr(Category, "order") else Category.objects.all()
    }