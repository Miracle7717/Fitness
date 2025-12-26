from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test
from functools import wraps

def role_required(*roles):
    """
    Декоратор для проверки роли пользователя
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())

            if request.user.role not in roles:
                raise PermissionDenied("У вас нет прав для доступа к этой странице.")

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

admin_required = role_required('admin')
manager_required = role_required('admin', 'manager')
trainer_required = role_required('trainer')
reception_required = role_required('reception')

def admin_or_manager_required(view_func):
    return role_required('admin', 'manager')(view_func)

def manager_or_trainer_required(view_func):
    return role_required('admin', 'manager', 'trainer')(view_func)

def all_staff_required(view_func):
    return role_required('admin', 'manager', 'trainer', 'reception')(view_func)