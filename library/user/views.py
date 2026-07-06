from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import CustomUser, Reader, Employee
from app.models import BorrowRecord

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.role == CustomUser.EMPLOYEE:
            return redirect("/admin/")
        return redirect("reader_dashboard")
    
    if request.method == "POST":
        identifier = request.POST.get("identifier").strip()
        password = request.POST.get("password")
        user_obj = CustomUser.objects.filter(username=identifier).first() or CustomUser.objects.filter(email=identifier).first()

        if user_obj is None:
            messages.error(request, "No account found with this username or email.")
            return render(request, "sign_in.html")
        
        user = authenticate(request, username=user_obj.username, password=password)
        if user is None:
            messages.error(request, "Incorrect password.")
            return render(request, "sign_in.html")

        if not user.is_active:
            messages.warning(request, "Your account is waiting for approval.")
            return render(request, "sign_in.html")

        login(request, user)
        if user.is_superuser or user.role == CustomUser.EMPLOYEE:
            return redirect("/admin/")
        return redirect("reader_dashboard")
    
    return render(request, "sign_in.html")


def reader_signup(request):
    if request.method == "POST":
        username = request.POST["username"].strip()
        email = request.POST["email"].strip()
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]
        roll_number = request.POST["roll_number"].strip()
        department = request.POST["department"].strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
        elif CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        elif Reader.objects.filter(roll_number=roll_number).exists():
            messages.error(request, "Roll number already exists.")
        else:
            try:
                validate_password(password1)
            except ValidationError as e:
                for error in e.messages:
                    messages.error(request, error)
                return render(request, "sign_up.html")

            user = CustomUser.objects.create_user(username=username, email=email, password=password1, role=CustomUser.READER, is_active=True)
            Reader.objects.create(user=user, roll_number=roll_number, department=department, phone=phone, address=address)
            messages.success(request, "Registration successful.")
        return render(request, "sign_up.html")
    return render(request, "sign_up.html")


def employee_signup(request):
    if request.method == "POST":
        username = request.POST["username"].strip()
        email = request.POST["email"].strip()
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]
        employee_id = request.POST["employee_id"].strip()
        designation = request.POST["designation"].strip()

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
        elif CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        elif Employee.objects.filter(employee_id=employee_id).exists():
            messages.error(request, "Employee ID already exists.")
        else:
            try:
                validate_password(password1)
            except ValidationError as e:
                for error in e.messages:
                    messages.error(request, error)
                return render(request, "emp_signup.html")

            user = CustomUser.objects.create_user(username=username, email=email, password=password1, role=CustomUser.EMPLOYEE, is_active=False)
            Employee.objects.create(user=user, employee_id=employee_id, designation=designation)
            messages.success(request, "Registration submitted successfully. Your account is pending administrator approval.")
            return render(request, "emp_pending.html")
        return render(request, "emp_signup.html")
    return render(request, "emp_signup.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required(login_url='/user/signin/')
def reader_dashboard(request):
    reader = Reader.objects.filter(user=request.user).first()
    if not reader:
        return render(request, "reader_dashboard.html", {"error": "Reader profile not found."})

    records = BorrowRecord.objects.filter(reader=reader).select_related('book')
    active_loans = records.filter(status__in=["Issued", "Overdue"])
    total_fines = sum(record.current_fine for record in records)

    context = {"records": records, "active_count": active_loans.count(), "total_fines": total_fines, "reader": reader}
    return render(request, "reader_dashboard.html", context)


@login_required
def profile(request):
    return render(request, "profile.html", {"user": request.user})


@login_required
def approve_employee(request, employee_id):
    if not (request.user.is_superuser or request.user.role == CustomUser.EMPLOYEE):
        return redirect("/")

    try:
        employee = Employee.objects.get(pk=employee_id)
    except Employee.DoesNotExist:
        messages.error(request, "Employee not found.")
        return redirect("/admin/")

    employee.user.is_active = True
    employee.user.save()
    messages.success(request, "Employee approved successfully.")
    return redirect("/admin/")