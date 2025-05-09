from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import Employee
from django.contrib.auth.decorators import login_required   


def register_employee(request):
    if request.method == 'POST':
        full_name = request.POST['full_name']
        email = request.POST['email']
        phone = request.POST['phone']
        position = request.POST['position']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('employee_register')

        # Check if email already exists
        if Employee.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('employee_register')

        # Create the employee
        employee = Employee(
            full_name=full_name,
            email=email,
            phone=phone,
            position=position,
            role='employee',  # Default role is 'employee'
            password=make_password(password),  # Encrypt password
            is_active=True,  # Employee is active by default
            is_staff=False,  # Not staff by default
        )
        employee.save()

        # Success message and redirect to login
        messages.success(request, "Registration successful! Please login.")
        return redirect('master_dashboard')

    return render(request, 'attendance/register.html')


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Employee

def login_employee(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate using email and password
        user = authenticate(request, email=email, password=password)

        if user is not None:
            if user.is_active:  # Check if the user is active
                login(request, user)

                if user.role == 'admin':
                    return redirect('master_dashboard')  # You should define this URL and view
                else:
                    return redirect('employee_dashboard')  # You should define this URL and view
            else:
                messages.error(request, "Your account is inactive. Please contact admin.")
                return redirect('employee_login')
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('login_employee')

    return render(request, 'attendance/login.html')

from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect

def logout(request):
    # First logout the user
    auth_logout(request)
    
    # Then flush the entire session data
    request.session.flush()

    # Optional: clear important cookies manually if any
    response = redirect('login_employee')
    response.delete_cookie('sessionid')  # Delete session cookie
    response.delete_cookie('csrftoken')   # Delete CSRF cookie if needed

    return response

@login_required
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'attendance/employee_list.html', {'employees': employees})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import EmployeeAttendance
from datetime import datetime, timedelta

@login_required
def employee_dashboard(request):
    employee = request.user
    attendances = EmployeeAttendance.objects.filter(employee=employee).order_by('-date')

    total_days_worked = attendances.count()

    total_work_hours = timedelta()
    for attendance in attendances:
        if attendance.check_in_time and attendance.check_out_time:
            check_in = datetime.combine(attendance.date, attendance.check_in_time)
            check_out = datetime.combine(attendance.date, attendance.check_out_time)
            total_work_hours += (check_out - check_in)

    # Prepare data for graph
    graph_labels = [att.date.strftime('%d %b') for att in attendances]
    graph_data = []
    for att in attendances:
        if att.check_in_time and att.check_out_time:
            start = datetime.combine(att.date, att.check_in_time)
            end = datetime.combine(att.date, att.check_out_time)
            worked_hours = (end - start).seconds / 3600  # convert seconds to hours
            graph_data.append(round(worked_hours, 2))
        else:
            graph_data.append(0)

    context = {
        'employee': employee,
        'attendances': attendances,
        'total_days_worked': total_days_worked,
        'total_work_hours': total_work_hours,
        'graph_labels': graph_labels[::-1],  # Reverse for recent first
        'graph_data': graph_data[::-1],
    }
    return render(request, 'attendance/employee_dashboard.html', context)
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Employee, EmployeeAttendance, OfficeLocation

@login_required
def master_dashboard(request):
    # Get total employees
    total_employees = Employee.objects.count()

    # Get today's attendance count
    today = timezone.now().date()
    total_attendance = EmployeeAttendance.objects.filter(date=today).count()

    # Get office location details
    office_location = OfficeLocation.objects.first()

    context = {
        'total_employees': total_employees,
        'total_attendance': total_attendance,
        'office_location': office_location,
    }
    
    return render(request, 'attendance/admin_dashboard.html', context)


from django.shortcuts import render, redirect
from .models import EmployeeAttendance, Employee, OfficeLocation
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from math import radians, sin, cos, sqrt, atan2

# Haversine distance check
def is_within_office_range(emp_lat, emp_lon, office_lat, office_lon, allowed_radius=1.0):
    R = 6371.0  # Earth radius in kilometers
    emp_lat_rad, emp_lon_rad = radians(emp_lat), radians(emp_lon)
    office_lat_rad, office_lon_rad = radians(office_lat), radians(office_lon)
    dlat = office_lat_rad - emp_lat_rad
    dlon = office_lon_rad - emp_lon_rad
    a = sin(dlat/2)**2 + cos(emp_lat_rad) * cos(office_lat_rad) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance <= allowed_radius
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import EmployeeAttendance, OfficeLocation, OfficeSettings
from datetime import datetime, timedelta
from math import radians, cos, sin, asin, sqrt

def haversine(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of Earth in kilometers
    return c * r


@login_required
def mark_attendance(request):
    if request.method == 'POST':
        employee = request.user
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        photo = request.FILES.get('photo')
        device_time_str = request.POST.get('device_time')
        gps_status = request.POST.get('gps_status')
        network_status = request.POST.get('network_status')

        if gps_status != 'enabled':
            messages.error(request, "GPS must be enabled to mark attendance.")
            return redirect('mark_attendance')

        if network_status != 'online':
            messages.error(request, "You must be online to mark attendance.")
            return redirect('mark_attendance')

        if not latitude or not longitude:
            messages.error(request, "Location access is required to mark attendance.")
            return redirect('mark_attendance')

        if not device_time_str:
            messages.error(request, "Device time not provided.")
            return redirect('mark_attendance')

        try:
            device_time = datetime.strptime(device_time_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            messages.error(request, "Invalid device time format.")
            return redirect('mark_attendance')

        today = timezone.localdate()
        office_settings = OfficeSettings.objects.first()
        office_location = OfficeLocation.objects.first()

        # GPS Validation
        distance = haversine(float(latitude), float(longitude),
                             float(office_location.latitude), float(office_location.longitude))
        if distance > office_location.allowed_range_km:
            messages.error(request, f"You are outside the allowed office range ({office_location.allowed_range_km} km). Current distance: {distance:.2f} km")
            return redirect('mark_attendance')

        # Attendance Logic
        attendance_record = EmployeeAttendance.objects.filter(employee=employee, date=today).first()

        if not attendance_record:
            # Mark Check-in (use device time)
            grace_time = (datetime.combine(today, office_settings.working_start_time) + timedelta(minutes=office_settings.grace_minutes)).time()
            is_late = device_time.time() > grace_time

            EmployeeAttendance.objects.create(
                employee=employee,
                date=today,
                check_in_time=device_time.time(),
                latitude=latitude,
                longitude=longitude,
                photo=photo,
                is_late=is_late
            )
            messages.success(request, f"Check-in marked successfully at {device_time.strftime('%I:%M %p')} {'(Late)' if is_late else ''}")
        else:
            if attendance_record.check_out_time:
                messages.warning(request, "You have already completed both Check-in and Check-out today.")
            else:
                # Mark Check-out (use device time)
                attendance_record.check_out_time = device_time.time()

                # Compare device_time with office working_end_time
                if device_time.time() < office_settings.working_end_time:
                    attendance_record.is_early_out = True
                else:
                    attendance_record.is_early_out = False

                attendance_record.save()

                if attendance_record.is_early_out:
                    messages.success(request, f"Check-out marked at {device_time.strftime('%I:%M %p')} (Early Out).")
                else:
                    messages.success(request, f"Check-out marked at {device_time.strftime('%I:%M %p')}.")

        return redirect('mark_attendance')

    return render(request, 'attendance/mark_attendance.html')

from math import radians, sin, cos, sqrt, atan2

# Radius of the Earth in kilometers
R = 6371.0

def is_within_office_range(employee_lat, employee_lon, office_lat, office_lon, allowed_radius=1.0):
    """
    Check if employee's location is within a certain distance (default 1 km) of the office.
    """
    # Convert latitude and longitude from degrees to radians
    employee_lat_rad = radians(employee_lat)
    employee_lon_rad = radians(employee_lon)
    office_lat_rad = radians(office_lat)
    office_lon_rad = radians(office_lon)

    # Haversine formula
    dlat = office_lat_rad - employee_lat_rad
    dlon = office_lon_rad - employee_lon_rad

    a = sin(dlat / 2)**2 + cos(employee_lat_rad) * cos(office_lat_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c  # in kilometers

    # Return if distance is within allowed radius
    return distance <= allowed_radius




from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from .models import OfficeSettings, OfficeLocation

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@user_passes_test(is_admin)
def working_hourse(request):
    settings = OfficeSettings.objects.first()

    if request.method == 'POST':
        working_start_time = request.POST.get('working_start_time')
        working_end_time = request.POST.get('working_end_time')
        grace_minutes = request.POST.get('grace_minutes')

        if settings:
            settings.working_start_time = working_start_time
            settings.working_end_time = working_end_time
            settings.grace_minutes = grace_minutes
            settings.save()
        else:
            OfficeSettings.objects.create(
                working_start_time=working_start_time,
                working_end_time=working_end_time,
                grace_minutes=grace_minutes
            )

        messages.success(request, "Office working hours updated successfully.")
        return redirect('office_location')

    return render(request, 'attendance/working_hourse.html', {'settings': settings})

@user_passes_test(is_admin)
def office_location(request):
    location = OfficeLocation.objects.first()

    if request.method == 'POST':
        name = request.POST.get('name')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        allowed_range_km = request.POST.get('allowed_range_km')

        if location:
            location.name = name
            location.latitude = latitude
            location.longitude = longitude
            location.allowed_range_km = allowed_range_km
            location.save()
        else:
            OfficeLocation.objects.create(
                name=name,
                latitude=latitude,
                longitude=longitude,
                allowed_range_km=allowed_range_km
            )

        messages.success(request, "Office location updated successfully.")
        return redirect('office_location')

    return render(request, 'attendance/office_location.html', {'location': location})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Employee

# Edit Employee (without forms.py)
def edit_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        position = request.POST.get('position')
        department = request.POST.get('department')
        role = request.POST.get('role')
        date_of_joining = request.POST.get('date_of_joining')
        
        # Update employee fields
        employee.full_name = full_name
        employee.email = email
        employee.phone = phone
        employee.position = position
        employee.department = department
        employee.role = role
        employee.date_of_joining = date_of_joining
        
        employee.save()
        messages.success(request, 'Employee updated successfully.')
        return redirect('employee_list')
    
    return render(request, 'attendance/edit_employee.html', {'employee': employee})


# Delete Employee (same)
def delete_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'Employee deleted successfully.')
        return redirect('employee_list')
    
    return render(request, 'attendance/confirm_delete.html', {'employee': employee})


# views.py
from django.shortcuts import render
from django.utils import timezone
from .models import EmployeeAttendance, Employee

def employees_present_on_date(request):
    employees = Employee.objects.all()
    attendance_records = []
    selected_date = None

    if request.method == 'POST':
        selected_date = request.POST.get('date')
        if selected_date:
            # Convert the selected date to a datetime object
            selected_date = timezone.datetime.strptime(selected_date, '%Y-%m-%d').date()

            # Filter attendance records by selected date
            attendance_records = EmployeeAttendance.objects.filter(date=selected_date)

            # Check if the employees are present (i.e., have check-in time)
            employees_present = []
            for employee in employees:
                attendance = attendance_records.filter(employee=employee).first()
                if attendance and attendance.check_in_time:  # Check if employee is present
                    employees_present.append({
                        'employee': employee,
                        'attendance': attendance
                    })

            return render(request, 'attendance/employees_present_on_date.html', {
                'employees_present': employees_present,
                'selected_date': selected_date
            })
    return render(request, 'attendance/employees_present_on_date.html', {
        'employees_present': [],
        'selected_date': selected_date
    })



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import EmployeeAttendance, Employee
from datetime import datetime

@login_required
def correct_attendance(request, attendance_id):
    # Ensure only admin users can access this view
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to correct attendance.")
        return redirect('home')

    # Fetch the attendance record by ID
    attendance = get_object_or_404(EmployeeAttendance, id=attendance_id)

    if request.method == 'POST':
        check_in_time_str = request.POST.get('check_in_time')
        check_out_time_str = request.POST.get('check_out_time')
        is_late = 'is_late' in request.POST
        is_early_out = 'is_early_out' in request.POST

        if check_in_time_str:
            try:
                attendance.check_in_time = datetime.strptime(check_in_time_str, '%H:%M').time()
            except ValueError:
                messages.error(request, "Invalid check-in time format. Use HH:MM.")
                return redirect('correct_attendance', attendance_id=attendance_id)

        if check_out_time_str:
            try:
                attendance.check_out_time = datetime.strptime(check_out_time_str, '%H:%M').time()
            except ValueError:
                messages.error(request, "Invalid check-out time format. Use HH:MM.")
                return redirect('correct_attendance', attendance_id=attendance_id)

        attendance.is_late = is_late
        attendance.is_early_out = is_early_out

        attendance.save()

        messages.success(request, "Attendance record corrected successfully.")
        return redirect('employees_present_on_date')

    return render(request, 'attendance/correct_attandence.html', {'attendance': attendance})



from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import render
import csv
from .models import EmployeeAttendance

@staff_member_required
def export_attendance_csv(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        attendances = EmployeeAttendance.objects.all().order_by('-date')

        if start_date and end_date:
            attendances = attendances.filter(date__range=[start_date, end_date])

        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="attendance.csv"'

        writer = csv.writer(response)

        # Write the header row
        writer.writerow(['Employee Name', 'Email', 'Date', 'Check-In Time', 'Check-Out Time', 'Latitude', 'Longitude', 'Is Late', 'Is Early Out'])

        # Write data rows
        for attendance in attendances:
            writer.writerow([
                attendance.employee.full_name,
                attendance.employee.email,
                attendance.date.strftime('%Y-%m-%d'),
                attendance.check_in_time.strftime('%H:%M:%S') if attendance.check_in_time else '',
                attendance.check_out_time.strftime('%H:%M:%S') if attendance.check_out_time else '',
                attendance.latitude if attendance.latitude else '',
                attendance.longitude if attendance.longitude else '',
                'Yes' if attendance.is_late else 'No',
                'Yes' if attendance.is_early_out else 'No',
            ])

        return response

    return render(request, 'attendance/export_attendance.html')  # Show date form if GET request





from django.shortcuts import render, get_object_or_404
from .models import Employee, EmployeeAttendance

def employee_attendance_history(request, emp_id):
    employee = get_object_or_404(Employee, id=emp_id)
    attendance_records = EmployeeAttendance.objects.filter(employee=employee).order_by('date')

    # Group attendance month-wise
    month_summary = {}
    for record in attendance_records:
        month = record.date.strftime('%B %Y')  # Example: "April 2025"
        if month not in month_summary:
            month_summary[month] = []
        month_summary[month].append(record)

    context = {
        'employee': employee,
        'month_summary': month_summary,
    }
    return render(request, 'attendance/employee_attendance_history.html', context)
