# accounts/context_processors.py

def sidebar_roles(request):
    """
    Returns the current user's role code for sidebar visibility.
    """
    if request.user.is_authenticated:
        # return the role code as string: 'ADMIN', 'MANAGER', 'EMPLOYEE'
        return {'role': request.user.userprofile.role.role_code}
    return {'role': None}

def user_role(request):
    if request.user.is_authenticated:
        # Superuser ALWAYS treated as ADMIN
        if request.user.is_superuser:
            return {'role': 'ADMIN'}

        return {'role': request.user.userprofile.role.role_code}

    return {}
