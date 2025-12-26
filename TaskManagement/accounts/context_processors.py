def sidebar_roles(request):
    if request.user.is_authenticated:
        try:
            role = request.user.userprofile.role
        except:
            role = None

        return {
            'role': role,
            'is_admin': role == 'ADMIN',
            'is_manager': role == 'MANAGER',
            'is_employee': role == 'EMPLOYEE',
        }
    return {}
