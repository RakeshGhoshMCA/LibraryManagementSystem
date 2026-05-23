from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/upload-book/', views.upload_book_api, name='upload_book_api'),
]

