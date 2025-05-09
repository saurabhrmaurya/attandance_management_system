from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Employee, EmployeeAttendance, OfficeLocation

class EmployeeAdmin(BaseUserAdmin):
    list_display = ('email', 'full_name', 'phone', 'position', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'full_name', 'phone', 'position')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'phone', 'position')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'phone', 'position', 'role', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

admin.site.register(Employee, EmployeeAdmin)

@admin.register(EmployeeAttendance)
class EmployeeAttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'check_in_time', 'check_out_time', 'is_late', 'is_early_out')
    list_filter = ('date', 'is_late', 'is_early_out')
    search_fields = ('employee__full_name', 'employee__email')

@admin.register(OfficeLocation)
class OfficeLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude', 'allowed_range_km')
    search_fields = ('name',)
