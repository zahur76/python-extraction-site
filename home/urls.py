from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [    
    path('', views.home, name='home'),    
    path('main', views.extractor, name='extractor'),
    path('product_details/<int:product_id>', views.product_details, name='product_details'),
    path('database/', views.database, name='database'),
    path('save_database', views.save_database, name='save_database'),
    path('data_view', views.data_view, name='data_view'),
    path('previous_run/<int:run_id>', views.previous_run, name='previous_run'),
]     
