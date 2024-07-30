from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from pic.models import User, AccountManager, Customer, ServiceProvider

class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('username', 'user_type')
    fieldsets = (
        (None, {'fields': ('username', 'password', 'user_type')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('username', 'user_type', 'password1', 'password2')}),
    )

admin.site.register(User, UserAdmin)
admin.site.register(AccountManager)
admin.site.register(Customer)
admin.site.register(ServiceProvider)