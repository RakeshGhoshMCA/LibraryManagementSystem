from datetime import date, timedelta
from decimal import Decimal
from django.db import models
from django.db.models import F
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

class Book(models.Model):
    LANGUAGE_CHOICES = [
        ("English", "English"),
        ("Bengali", "Bengali"),
        ("Hindi", "Hindi"),
        ("Other", "Other"),
    ]

    AUDIENCE_CHOICES = [
        ("Children", "Children"),
        ("Students", "Students"),
        ("Research", "Research"),
        ("General", "General"),
        ("Adult", "Adult"),
        ("Others", "Others"),
    ]

    GENRE_CHOICES = [
        ("Classic", "Classic"),
        ("Fiction", "Fiction"),
        ("Dystopian", "Dystopian"),
        ("Romance", "Romance"),
        ("Fantasy", "Fantasy"),
        ("Non-Fiction", "Non-Fiction"),
        ("Psychology", "Psychology"),
        ("Business", "Business"),
        ("Self-Help", "Self-Help"),
        ("Thriller", "Thriller"),
        ("Sci-Fi", "Sci-Fi"),
        ("Historical Fiction", "Historical Fiction"),
        ("Poetry", "Poetry"),
        ("Drama", "Drama"),
        ("Gothic", "Gothic"),
        ("Philosophical", "Philosophical"),
        ("Others", "Others"),
    ]

    SUBJECT_CHOICES = [
        ("Literature", "Literature"),
        ("History", "History"),
        ("Geography", "Geography"),
        ("Mathematics", "Mathematics"),
        ("Physics", "Physics"),
        ("Chemistry", "Chemistry"),
        ("Biology", "Biology"),
        ("Computer Science", "Computer Science"),
        ("Artificial Intelligence", "Artificial Intelligence"),
        ("Machine Learning", "Machine Learning"),
        ("Data Science", "Data Science"),
        ("Economics", "Economics"),
        ("Business Studies", "Business Studies"),
        ("Commerce", "Commerce"),
        ("Accounting", "Accounting"),
        ("Finance", "Finance"),
        ("Political Science", "Political Science"),
        ("Sociology", "Sociology"),
        ("Psychology", "Psychology"),
        ("Philosophy", "Philosophy"),
        ("Law", "Law"),
        ("Education", "Education"),
        ("Environmental Science", "Environmental Science"),
        ("Engineering", "Engineering"),
        ("Electronics", "Electronics"),
        ("Mechanical Engineering", "Mechanical Engineering"),
        ("Civil Engineering", "Civil Engineering"),
        ("Medical Science", "Medical Science"),
        ("Nursing", "Nursing"),
        ("Agriculture", "Agriculture"),
        ("Astronomy", "Astronomy"),
        ("Statistics", "Statistics"),
        ("Linguistics", "Linguistics"),
        ("Religion", "Religion"),
        ("Art", "Art"),
        ("Music", "Music"),
        ("Drama", "Drama"),
        ("Sports", "Sports"),
        ("General Knowledge", "General Knowledge"),
        ("Children", "Children"),
        ("Technology", "Technology"),
        ("Others", "Others"),
    ]

    SHELF_CHOICES = [
        (f"Shelf {letter}-{number}", f"Shelf {letter}-{number}")
        for letter in ["A", "B", "C", "D", "E", "F"]
        for number in range(1, 11)
    ]

    REMARKS_CHOICES = [
        ("Good Condition", "Good Condition"),
        ("Needs Binding", "Needs Binding"),
        ("Damaged", "Damaged"),
    ]

    STATUS_CHOICES = [
        ("Available", "Available"),
        ("Unavailable", "Unavailable"),
        ("Lost", "Lost"),
        ("Damaged", "Damaged"),
    ]

    title = models.CharField(max_length=100, db_index=True)
    authors = models.CharField(max_length=500, help_text="Separate multiple authors with commas.")
    isbn = models.CharField(max_length=17, unique=True, db_index=True)
    publisher = models.CharField(max_length=100)
    publication_year = models.IntegerField(validators=[MinValueValidator(1454), MaxValueValidator(date.today().year)])
    edition = models.PositiveSmallIntegerField(blank=True, null=True)
    language = models.CharField(max_length=50, choices=LANGUAGE_CHOICES)
    genre = models.CharField(max_length=100, choices=GENRE_CHOICES)
    subject = models.CharField(max_length=100, choices=SUBJECT_CHOICES, blank=True, null=True)
    audience = models.CharField(max_length=50, choices=AUDIENCE_CHOICES)
    accession_number = models.CharField(max_length=20, unique=True, db_index=True)
    location_shelf = models.CharField(max_length=50, choices=SHELF_CHOICES)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    image = models.ImageField(upload_to="books/")
    remarks = models.CharField(max_length=100, choices=REMARKS_CHOICES, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Available")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.isbn})"


class BorrowRecord(models.Model):
    STATUS_CHOICES = [
        ("Issued", "Issued"),
        ("Returned", "Returned"),
        ("Overdue", "Overdue"),
    ]

    reader = models.ForeignKey("user.Reader", on_delete=models.CASCADE, related_name="borrow_records")
    book = models.ForeignKey("Book", on_delete=models.CASCADE, related_name="borrow_records")
    issued_by = models.ForeignKey("user.Employee", on_delete=models.SET_NULL, null=True, blank=True, related_name="managed_issues")
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField(blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)
    fine = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Issued")
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-issue_date"]

    def save(self, *args, **kwargs):
        creating = self.pk is None

        if not self.due_date:
            self.due_date = self.issue_date + timedelta(days=14)

        if creating:
            if self.book.available_copies <= 0:
                raise ValidationError("No copies of this book are currently available.")

            already_issued = BorrowRecord.objects.filter(reader=self.reader, book=self.book, status__in=["Issued", "Overdue"]).exists()
            if already_issued:
                raise ValidationError("This reader already has an active copy of this book.")

            self.book.available_copies = F('available_copies') - 1
            self.book.save(update_fields=['available_copies'])
            self.book.refresh_from_db()
        else:
            original = BorrowRecord.objects.get(pk=self.pk)

            if original.status != "Returned" and self.status == "Returned":
                self.return_date = timezone.now().date()
                self.book.available_copies = F('available_copies') + 1
                self.book.save(update_fields=['available_copies'])
                self.book.refresh_from_db()

                if self.return_date > self.due_date:
                    late_days = (self.return_date - self.due_date).days
                    self.fine = late_days * 2

        if self.status == "Issued" and timezone.now().date() > self.due_date:
            self.status = "Overdue"

        super().save(*args, **kwargs)
    
    @property
    def current_fine(self):
        if self.status == "Returned":
            return self.fine
        
        today = timezone.now().date()
        if today > self.due_date:
            late_days = (today - self.due_date).days
            return late_days * 2
        return 0.00

    def __str__(self):
        admin_user = self.issued_by.user.username if self.issued_by else "System"
        return f"{self.reader.user.username} -> {self.book.title} (By: {admin_user})"