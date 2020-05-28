from django.shortcuts import redirect


def unauthenticated_user(view_func):
    def wrapper_func(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('questions:index')
        else:
            return view_func(self, request, *args, **kwargs)
    return wrapper_func


def staff_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_staff:
            return redirect('questions:index')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func
