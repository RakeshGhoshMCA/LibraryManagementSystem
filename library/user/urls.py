from django.urls import path
from . import views

urlpatterns = [

    path("signin/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("signup/", views.reader_signup, name="signup"),
    path("employee-signup/", views.employee_signup, name="employee_signup"),

    path("dashboard/",views.reader_dashboard,name="reader_dashboard"),
    path("profile/",views.profile,name="profile"),

    path("approve-employee/<int:employee_id>/",views.approve_employee,name="approve_employee"),
]