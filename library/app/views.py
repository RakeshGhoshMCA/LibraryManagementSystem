from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Book

@csrf_exempt
def upload_book_api(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Only POST requests allowed'}, status=405)

    try:
        title = request.POST.get('title')
        isbn = request.POST.get('isbn')
        accession_number = request.POST.get('accession_number')
        
        if Book.objects.filter(isbn=isbn).exists():
            return JsonResponse({'status': 'error', 'message': f'ISBN {isbn} already exists.'}, status=400)
            
        if Book.objects.filter(accession_number=accession_number).exists():
            return JsonResponse({'status': 'error', 'message': f'Accession Number {accession_number} already exists.'}, status=400)

        uploaded_image = request.FILES.get('image')
        if not uploaded_image:
            return JsonResponse({'status': 'error', 'message': f'Missing image file for book: {title}'}, status=400)

        book = Book(
            title=title,
            authors=request.POST.get('authors'),
            isbn=isbn,
            publisher=request.POST.get('publisher'),
            publication_year=int(request.POST.get('publication_year')),
            edition=int(request.POST.get('edition')) if request.POST.get('edition') else None,
            language=request.POST.get('language'),
            genre=request.POST.get('genre'),
            subject=request.POST.get('subject'),
            audience=request.POST.get('audience'),
            accession_number=accession_number,
            location_shelf=request.POST.get('location_shelf'),
            number_of_copies=int(request.POST.get('number_of_copies', 1)),
            price=request.POST.get('price'),
            image=uploaded_image,
            remarks=request.POST.get('remarks')
        )

        book.full_clean() 
        print(book)
        print()

        return JsonResponse({
            'status': 'success', 
            'message': f'Successfully uploaded "{title}" (ID: {book.id})'
        }, status=201)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    

def home(request):
    page = {"name" : "home"}
    data = {
        "name": "Snehasish",
        "course": "MCA",
        "skills": ["Python","Django","React"]
    }

    return render(request,'home.html',context = { "data" : data, "page" : page})