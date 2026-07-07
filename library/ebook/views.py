from django.shortcuts import render
from .models import EBook
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import EBook

def ebook_list(request):
    return render(request, "ebooks.html", {"ebooks": EBook.objects.all()})

@csrf_exempt
def upload_bulk(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        title = request.POST.get("title")
        author = request.POST.get("author")
        cover_image = request.FILES.get("cover_image")
        pdf_file = request.FILES.get("pdf_file")

        if not all([title, author, cover_image, pdf_file]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        ebook = EBook.objects.create(title=title, author=author, cover_image=cover_image, pdf_file=pdf_file)
        return JsonResponse({"message": f"Successfully uploaded: {ebook.title}"}, status=201)


    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)