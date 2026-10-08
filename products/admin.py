
# Register your models here.
from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    list_filter = ('parent',)
    search_fields = ('name',)


class ProductAdmin(admin.ModelAdmin):
    # Admin table me yeh columns dikhenge
    list_display = ('name', 'category', 'price', 'stock', 'is_available', 'created_at')
    # In fields ko list view se hi edit kiya ja sakega
    list_editable = ('price', 'stock', 'is_available')
    # Search bar add karna
    search_fields = ('name', 'description')
    list_filter = ('category', 'is_available')

admin.site.register(Product, ProductAdmin)