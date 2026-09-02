
# Register your models here.
from django.contrib import admin
from .models import Product

class ProductAdmin(admin.ModelAdmin):
    # Admin table me yeh columns dikhenge
    list_display = ('name', 'price', 'stock', 'is_available', 'created_at')
    # In fields ko list view se hi edit kiya ja sakega
    list_editable = ('price', 'stock', 'is_available')
    # Search bar add karna
    search_fields = ('name', 'description')

admin.site.register(Product, ProductAdmin)