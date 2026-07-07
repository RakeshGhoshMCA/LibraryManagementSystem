from django.contrib import admin
from django.utils.html import format_html
from .models import Book, BorrowRecord

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "authors", "isbn", "publisher", "available_copies", "total_copies", "status", "location_shelf")
    search_fields = ("title", "authors", "isbn", "publisher", "accession_number")
    list_filter = ("language", "genre", "subject", "status")
    ordering = ("title",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ("reader_link", "book_link", "issue_date", "due_date", "return_date", "fine_display", "status_badge", "issued_by")
    list_filter = ("status", "issue_date", "due_date")
    search_fields = ("reader__user__username", "reader__user__first_name", "book__title", "issued_by__user__username")
    readonly_fields = ("return_date", "fine", "created_at", "updated_at")
    
    fieldsets = (
        ("Core Information", {"fields": ("reader", "book", "issued_by", "status")}),
        ("Timeline", {"fields": ("issue_date", "due_date", "return_date")}),
        ("Financials & Notes", {"fields": ("fine", "remarks")}),
        ("Metadata", {"classes": ("collapse",), "fields": ("created_at", "updated_at")}),
    )

    def save_model(self, request, obj, form, change):
        if not change and hasattr(request.user, 'employee_profile'):
            obj.issued_by = request.user.employee_profile
        super().save_model(request, obj, form, change)

    def status_badge(self, obj):
        colors = {"Issued": "#26a69a", "Returned": "#66bb6a", "Overdue": "#ef5350"}
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
            colors.get(obj.status, "#757575"), obj.status
        )
    status_badge.short_description = "Status"

    def fine_display(self, obj):
        if obj.fine > 0:
            return format_html('<strong style="color: #ef5350;">${}</strong>', obj.fine)
        return f"${obj.fine}"
    fine_display.short_description = "Fine"

    def reader_link(self, obj):
        return obj.reader.user.get_full_name() or obj.reader.user.username
    reader_link.short_description = "Reader"

    def book_link(self, obj):
        return obj.book.title
    book_link.short_description = "Book"