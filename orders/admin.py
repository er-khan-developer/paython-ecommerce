from django.contrib import admin
from .models import Order, OrderItem



# OrderItem ko Order ke andar table ki tarah dikhane ke liye
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'price', 'quantity', 'get_total_price')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'is_paid', 'created_at')
    list_filter = ('is_paid', 'created_at')
    inlines = [OrderItemInline] # Inline add kar diya

admin.site.register(Order, OrderAdmin)
