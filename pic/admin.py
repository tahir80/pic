from django.contrib import admin
from pic.execution.models import Job
# Register your models here.
from django.contrib import admin
from pic.stat_analysis.models.report import Report
from pic.stat_analysis.models.statistics import JobReportResult, OrderReportResult
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from pic.models import User, AccountManager, Customer, ServiceProvider, \
    AccountManagerCustomer, Service, Order, AccountManagerService, ServiceOrder
from django import forms


admin.site.site_header = "PICS ADMIN PANEL"


class UserAdmin(admin.ModelAdmin):
    model = User

    search_fields = ('username', )

    list_display = ('username', 'user_type', 'email', 'phone')

    list_filter = ['user_type']

    list_display_links = ['username', 'user_type']

    list_editable = ('email', 'phone', )

    # fields = ('username',
              
    #           )


class AccountManagerCustomerForm(forms.ModelForm):
  
    class Meta:
        model = AccountManagerCustomer
        fields = ['f_am_id', 'f_cus_id', 'date_assigned']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Print the queryset for debugging
        print('AccountManager queryset:', AccountManager.objects.all())
        print('Customer queryset:', Customer.objects.all())

        account_managers = AccountManager.objects.all()
        customers = Customer.objects.all()


       # Get account manager and customer instances
        account_managers = AccountManager.objects.select_related('user').all()
        customers = Customer.objects.select_related('user').all()

        # Print the fetched AccountManager instances for debugging
        print('Account Managers:')
        for am in account_managers:
            user = am.user
            print(f'ID: {am.am_id}, Name: {user.username}, Email: {user.email}, Phone: {user.phone}')

        # Print the fetched Customer instances for debugging
        print('Customers:')
        for cus in customers:
            user = cus.user
            print(f'ID: {cus.cus_id}, Name: {user.username}, Email: {user.email}, Phone: {user.phone}')
        

        # Set choices for f_am_id
        self.fields['f_am_id'].choices = [
            (am.am_id, am.am_id) for am in account_managers
        ]

        # Set choices for f_cus_id
        self.fields['f_cus_id'].choices = [
            (cus.cus_id, cus.cus_id) for cus in customers
        ]


class AccountManagerCustomerAdmin(admin.ModelAdmin):
    form = AccountManagerCustomerForm
    list_display = ('am_cust_id', 'get_am_username', 'get_cus_username', 'date_assigned')

    def get_am_username(self, obj):
        return obj.f_am_id.user.username if obj.f_am_id and obj.f_am_id.user else 'No Account Manager'
    get_am_username.short_description = 'Account Manager Username'

    def get_cus_username(self, obj):
        return obj.f_cus_id.user.username if obj.f_cus_id and obj.f_cus_id.user else 'No Customer'
    get_cus_username.short_description = 'Customer Username'

admin.site.register(AccountManagerCustomer, AccountManagerCustomerAdmin)



class AccountManagerAdmin(admin.ModelAdmin):
    list_display = (
        'am_id', 
        'get_user_username', 
        'get_email', 
        'get_phone'
    )

    def get_user_username(self, obj):
        return obj.user.username if obj.user else None
    get_user_username.short_description = 'Username'

    def get_email(self, obj):
        return obj.user.email if obj.user else None
    get_email.short_description = 'Email'

    def get_phone(self, obj):
        return obj.user.phone if obj.user else None
    get_phone.short_description = 'Phone'

admin.site.register(AccountManager, AccountManagerAdmin)




class CustomerAdmin(admin.ModelAdmin):
    list_display = ('cus_id', 'get_user_username', 'get_phone', 'get_email')

    # Method to display the username of the Customer
    def get_user_username(self, obj):
        return obj.user.username if obj.user else None
    get_user_username.short_description = 'Username'  

    def get_phone(self, obj):
        return obj.user.phone if obj.user else None
    get_phone.short_description = 'Phone'

    def get_email(self, obj):
       return obj.user.email if obj.user else None
    get_email.short_description = 'Email'

admin.site.register(Customer, CustomerAdmin)

admin.site.register(User, UserAdmin)
# admin.site.register(AccountManager)
# admin.site.register(Customer)

class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('get_user_username', 'get_email', 'get_phone')

    # fields = ("name", "email", "phone", )
    def get_user_username(self, obj):
        return obj.user.username if obj.user else None
    get_user_username.short_description = 'Username'

    def get_phone(self, obj):
        return obj.user.phone if obj.user else None
    get_phone.short_description = 'Phone'

    def get_email(self, obj):
       return obj.user.email if obj.user else None
    get_email.short_description = 'Email'  

admin.site.register(ServiceProvider, ServiceProviderAdmin)
# admin.site.register(Status)
# admin.site.register(AccountManagerCustomer)


admin.site.register(Service)
admin.site.register(Order)
admin.site.register(AccountManagerService)
admin.site.register(ServiceOrder)
admin.site.register(Job)
admin.site.register(Report)
admin.site.register(JobReportResult)
admin.site.register(OrderReportResult)


