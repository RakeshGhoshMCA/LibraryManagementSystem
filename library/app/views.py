from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from .models import Book, BorrowRecord
from user.models import Reader

@csrf_exempt
def upload_book_api(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Only POST requests allowed."}, status=405)

    try:
        title = request.POST.get("title")
        isbn = request.POST.get("isbn")
        accession_number = request.POST.get("accession_number")

        if Book.objects.filter(isbn=isbn).exists():
            return JsonResponse({"status": "error", "message": "ISBN already exists."}, status=400)

        if Book.objects.filter(accession_number=accession_number).exists():
            return JsonResponse({"status": "error", "message": "Accession number already exists."}, status=400)

        image = request.FILES.get("image")
        if image is None:
            return JsonResponse({"status": "error", "message": "Image is required."}, status=400)

        book = Book.objects.create(
            title=title,
            authors=request.POST.get("authors"),
            isbn=isbn,
            publisher=request.POST.get("publisher"),
            publication_year=request.POST.get("publication_year"),
            edition=request.POST.get("edition") or None,
            language=request.POST.get("language"),
            genre=request.POST.get("genre"),
            subject=request.POST.get("subject"),
            audience=request.POST.get("audience"),
            accession_number=accession_number,
            location_shelf=request.POST.get("location_shelf"),
            total_copies=request.POST.get("number_of_copies", 1),
            price=request.POST.get("price"),
            image=image,
            remarks=request.POST.get("remarks"),
        )
        return JsonResponse({
                "status": "success",
                "message": "Book uploaded successfully.",
                "book_id": book.id
            },
            status=201
        )

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


def home(request):
    all_books = Book.objects.all()
    context = {
        "trending_books": all_books.filter(status="Available")[:6],
        "literature_books": all_books.filter(subject="Literature")[:6]
    }
    return render(request, "home.html", context)


def books(request):
    all_books = list(Book.objects.all())
    total_count = len(all_books)

    trending_books = [b for b in all_books if b.status == "Available"][:6]
    classic_books = [b for b in all_books if b.genre == "Classic"][:6]
    literature_books = [b for b in all_books if b.subject == "Literature"][:6]

    if not trending_books:
        trending_books = all_books[:6]
    if not classic_books:
        classic_books = all_books[6:12] if total_count > 6 else all_books
    if not literature_books:
        literature_books = all_books[12:18] if total_count > 12 else all_books
    
    context = {"trending_books": trending_books, "classic_books": classic_books, "literature_books": literature_books}
    return render(request, "books.html", context)


def book_details(request, id):
    book = get_object_or_404(Book, pk=id)
    return render(request, "book_details.html", {"book": book})


@login_required(login_url='/user/signin/')
def issue_book(request, id):
    book = get_object_or_404(Book, pk=id)
    
    try:
        reader = request.user.reader_profile
    except AttributeError:
        reader = Reader.objects.filter(user=request.user).first()
    
    if not reader:
        messages.error(request, "Authorization Error: Missing valid Reader record profile.")
        return redirect('books')

    issue_date = timezone.now().date()
    due_date = issue_date + timezone.timedelta(days=14)
    already_issued = BorrowRecord.objects.filter(reader=reader, book=book, status__in=["Issued", "Overdue"]).exists()

    if request.method == "POST":
        try:
            record = BorrowRecord(reader=reader, book=book, issue_date=issue_date, due_date=due_date, status="Issued")
            record.save()
            messages.success(request, f'Success! "{book.title}" has been issued. Please return by {due_date}.')
            return redirect('/user/dashboard/')
        except ValidationError as e:
            messages.error(request, e.message if hasattr(e, 'message') else str(e))
        except Exception as e:
            messages.error(request, f"Transaction aborted: {str(e)}")

    context = {"book": book, "reader": reader, "issue_date": issue_date, "due_date": due_date, "already_issued": already_issued}
    return render(request, "issue_book.html", context)

