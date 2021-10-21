from django.contrib import admin
from .models import Offers, Products, Offers
# Register your models here.

class ProductsAdmin(admin.ModelAdmin):
    # Admin display
        # Ordering in admin
    list_display = (
        'id',
        'product_name',  
    )
    ordering = ('id',)


class OffersAdmin(admin.ModelAdmin):
    # Admin display
        # Ordering in admin
    list_display = (
        'id',
        'seller_name',  
    )
    ordering = ('id',)

admin.site.register(Products, ProductsAdmin)
admin.site.register(Offers, OffersAdmin)

