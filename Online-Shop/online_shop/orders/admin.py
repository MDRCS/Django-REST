from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city', 'created', 'updated', 'paid']
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]


"""
You use a ModelInline class for the OrderItem model to include it as an inline in the OrderAdmin class.
An inline allows you to include a model on the same edit page as its related model.
"""

