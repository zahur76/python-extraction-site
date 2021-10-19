from django.contrib import admin
from .models import Products
# Register your models here.

class ProductsAdmin(admin.ModelAdmin):
    # Admin display
        # Ordering in admin
    list_display = (
        'id',  
    )
    ordering = ('pk',)
admin.site.register(Products, ProductsAdmin)

