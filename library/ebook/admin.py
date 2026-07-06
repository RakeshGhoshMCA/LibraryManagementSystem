from django.contrib import admin
from ebook.models import EBook

@admin.register(EBook)
class EBookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "cover_image", "pdf_file")
    search_fields = ("title", "author")