from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('register/', views.register_employee, name='employee_register'),
    path('', views.login_employee, name='login_employee'),
    path('logout/', views.logout, name='logout'),
    path('employees/', views.employee_list, name='employee_list'),

    #path('', views.attendance_page, name='attendance_page'),  # For your GPS attendance page
    path('mark/', views.mark_attendance, name='mark_attendance'),  # Already created before
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('masterdashboard/', views.master_dashboard, name='master_dashboard'),
    path('officeloaction/', views.office_location, name='office_location'),  # For your office location page
    path('workinghourse', views.working_hourse, name='working_hourse'), 
    path('employee/edit/<int:pk>/', views.edit_employee, name='edit_employee'),
    path('employee/delete/<int:pk>/', views.delete_employee, name='delete_employee'),
    path('employees_present/', views.employees_present_on_date, name='employees_present_on_date'),
     path('attendance/correct/<int:attendance_id>/', views.correct_attendance, name='correct_attendance'),
     path('export-csv/', views.export_attendance_csv, name='export_attendance_csv'),
     path('employee/<int:emp_id>/attendance-history/', views.employee_attendance_history, name='employee_attendance_history'),


# For your working hours page
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
