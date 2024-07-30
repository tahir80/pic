from django.contrib import admin
from pic.execution.models import Job
# Register your models here.
from django.contrib import admin
from pic.stat_analysis.models.report import Report
from pic.stat_analysis.models.statistics import JobReportResult, OrderReportResult
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from pic.models import User, AccountManager, Customer, ServiceProvider, Status, \
    AccountManagerCustomer, Service, Order, AccountManagerService, ServiceOrder


class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('username', 'user_type', 'email', 'phone') 

    fieldsets = (
        (None, {'fields': ('username', 'password', 'user_type', 'email', 'phone')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('username', 'user_type', 'password1', 'password2', 'email', 'phone')}),
    )

admin.site.register(User, UserAdmin)
admin.site.register(AccountManager)
admin.site.register(Customer)
admin.site.register(ServiceProvider)
admin.site.register(Status)
admin.site.register(AccountManagerCustomer)
admin.site.register(Service)
admin.site.register(Order)
admin.site.register(AccountManagerService)
admin.site.register(ServiceOrder)
admin.site.register(Job)
admin.site.register(Report)
admin.site.register(JobReportResult)
admin.site.register(OrderReportResult)


