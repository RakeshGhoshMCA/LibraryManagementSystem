from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date
from decimal import Decimal

class Book(models.Model):
    LANGUAGE_CHOICES = [
        ('English', 'English'),
        ('Bengali', 'Bengali'),
        ('Hindi', 'Hindi'),
        ('Other', 'Other'),
    ]

    AUDIENCE_CHOICES = [
        ('Children', 'Children'),
        ('Students', 'Students'),
        ('Research', 'Research'),
        ('General', 'General'),
        ('Adult', 'Adult'),
        ('others', 'others'),
    ]

    GENRE_CHOICES = [
        ('Classic', 'Classic'),
        ('Fiction', 'Fiction'),
        ('Dystopian', 'Dystopian'),
        ('Romance', 'Romance'),
        ('Fantasy', 'Fantasy'),
        ('Non-Fiction', 'Non-Fiction'),
        ('Psychology', 'Psychology'),
        ('Business', 'Business'),
        ('Self-Help', 'Self-Help'),
        ('Thriller', 'Thriller'),
        ('Sci-Fi', 'Sci-Fi'),
        ('Historical Fiction', 'Historical Fiction'),
        ('Poetry', 'Poetry'),
        ('Drama', 'Drama'),
        ('Gothic', 'Gothic'),
        ('Philosophical', 'Philosophical'),
        ('others', 'others'),
    ]

    SUBJECT_CHOICES = [
        ('Literature', 'Literature'),
        ('History', 'History'),
        ('Geography', 'Geography'),
        ('Mathematics', 'Mathematics'),
        ('Physics', 'Physics'),
        ('Chemistry', 'Chemistry'),
        ('Biology', 'Biology'),
        ('Computer Science', 'Computer Science'),
        ('Artificial Intelligence', 'Artificial Intelligence'),
        ('Machine Learning', 'Machine Learning'),
        ('Data Science', 'Data Science'),
        ('Economics', 'Economics'),
        ('Business Studies', 'Business Studies'),
        ('Commerce', 'Commerce'),
        ('Accounting', 'Accounting'),
        ('Finance', 'Finance'),
        ('Political Science', 'Political Science'),
        ('Sociology', 'Sociology'),
        ('Psychology', 'Psychology'),
        ('Philosophy', 'Philosophy'),
        ('Law', 'Law'),
        ('Education', 'Education'),
        ('Environmental Science', 'Environmental Science'),
        ('Engineering', 'Engineering'),
        ('Electronics', 'Electronics'),
        ('Mechanical Engineering', 'Mechanical Engineering'),
        ('Civil Engineering', 'Civil Engineering'),
        ('Medical Science', 'Medical Science'),
        ('Nursing', 'Nursing'),
        ('Agriculture', 'Agriculture'),
        ('Astronomy', 'Astronomy'),
        ('Statistics', 'Statistics'),
        ('Linguistics', 'Linguistics'),
        ('Religion', 'Religion'),
        ('Art', 'Art'),
        ('Music', 'Music'),
        ('Drama', 'Drama'),
        ('Sports', 'Sports'),
        ('General Knowledge', 'General Knowledge'),
        ('Children', 'Children'),
        ('Technology', 'Technology'),
        ('others', 'others'),
    ]
    SHELF_CHOICES = [
        (f"Shelf {letter}-{num}", f"Shelf {letter}-{num}")
        for letter in ['A', 'B', 'C', 'D']
        for num in range(1, 6)
    ]
    REMARKS_CHOICES = [
        ('Needs Binding', 'Needs Binding'),
        ('Good Condition', 'Good Condition'),
    ]

    title = models.CharField(max_length=100)
    authors = models.CharField(max_length=500,help_text="Multiple authors separated by commas")
    isbn = models.CharField(max_length=14,unique=True)
    publisher = models.CharField(max_length=100)
    publication_year = models.IntegerField(
        validators=[
            MinValueValidator(1454),
            MaxValueValidator(date.today().year)
        ]
    )
    edition = models.IntegerField(blank=True, null=True)
    language = models.CharField(max_length=50,choices=LANGUAGE_CHOICES)
    genre = models.CharField(max_length=100, choices=GENRE_CHOICES)
    subject = models.CharField(max_length=100, choices=SUBJECT_CHOICES, blank=True, null=True)
    audience = models.CharField(max_length=50,choices=AUDIENCE_CHOICES)
    accession_number = models.CharField(max_length=10,unique=True)
    location_shelf = models.CharField(max_length=50, choices=SHELF_CHOICES)
    number_of_copies = models.PositiveIntegerField(default=1)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal(0.00))
        ]

    )
    image = models.ImageField(upload_to='books/',blank=False,null=False)
    remarks = models.TextField(choices=REMARKS_CHOICES, blank=True,null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title