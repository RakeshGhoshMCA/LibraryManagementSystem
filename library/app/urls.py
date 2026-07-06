from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("books/", views.books, name="books"),
    path("book-details/<int:id>/", views.book_details, name="book_details"),
    path("issue-book/<int:id>/", views.issue_book, name="issue_book"),

    path("api/upload-book/", views.upload_book_api, name="upload_book_api"),
]