from django.apps import apps

def site_categories(request):
    Category = apps.get_model('products', 'Category')
    return {
        "categories": Category.objects.all().order_by("id")
    }

def user_avatar(request):
    """
    Trả về URL avatar nếu user đã đăng nhập và có avatar, ngược lại trả empty string.
    An toàn khi user.profile không tồn tại.
    """
    avatar_url = ""
    user = getattr(request, 'user', None)
    if user and user.is_authenticated:
        profile = getattr(user, 'profile', None)
        if profile:
            avatar = getattr(profile, 'avatar', None)
            # avatar có thể là ImageField/FileField, kiểm tra .url an toàn
            try:
                if avatar and getattr(avatar, 'url', None):
                    avatar_url = avatar.url
            except Exception:
                avatar_url = ""
    return {"user_avatar_url": avatar_url}