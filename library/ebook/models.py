from django.db import models

class EBook(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    cover_image = models.ImageField(upload_to="ebooks/covers/")
    pdf_file = models.FileField(upload_to="ebooks/pdfs/")

    def __str__(self):
        return self.title