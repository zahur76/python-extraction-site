from django.contrib import admin
from .models import Offers, Products, Offers, HistoryJson
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
        'products',
    )
    ordering = ('id',)

admin.site.register(Products, ProductsAdmin)
admin.site.register(Offers, OffersAdmin)
admin.site.register(HistoryJson)
