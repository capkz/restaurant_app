from django.contrib import admin
from .models import *

admin.site.register(Customer)
admin.site.register(Restaurant)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Shipping)
admin.site.register(Reviews)
admin.site.register(Discount_History)
