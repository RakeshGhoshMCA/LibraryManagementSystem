from django.urls import path
from . import views

urlpatterns = [
    path("", views.ebook_list, name="ebook_list"),

    path("api/upload-bulk/", views.upload_bulk, name="upload_bulk_api"),
]