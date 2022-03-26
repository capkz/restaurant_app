from django.http import HttpResponse
from django.shortcuts import redirect
from .models import *

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):

            print('Working', allowed_roles)
            
            my_type=None # am i customer or restaurant owner ?

            print(Customer.objects.get(name=request.user.username))


            return view_func(request, *args, **kwargs)
        return wrapper_func
    return decorator