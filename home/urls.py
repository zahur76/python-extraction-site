from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [    
    path('', views.home, name='home'),    
    path('main', views.extractor, name='extractor'),
    path('product_details/<int:product_id>', views.product_details, name='product_details'),
]