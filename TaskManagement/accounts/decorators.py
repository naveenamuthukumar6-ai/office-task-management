from django.shortcuts import redirect

def role_required(allowed_roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                if request.user.userprofile.role in allowed_roles:
                    return view_func(request, *args, **kwargs)
            return redirect('dashboard')
        return wrapper
    return decorator
