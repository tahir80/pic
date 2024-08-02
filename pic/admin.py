from django.contrib import admin
from pic.execution.models import Job
# Register your models here.
from django.contrib import admin
from pic.stat_analysis.models.report import Report
from pic.stat_analysis.models.statistics import JobReportResult, OrderReportResult, JobStatistics
from pic.stat_analysis.stat_utils import calculate_job_stats
from django.http import HttpResponse
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from pic.models import User, AccountManager, Customer, ServiceProvider, \
    AccountManagerCustomer, Service, Order, AccountManagerService, ServiceOrder, UserStatistics
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

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'f_sp_id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fetch Service Providers and populate choices for f_sp_id
        service_providers = ServiceProvider.objects.all()

        # Print the fetched ServiceProvider instances for debugging
        print('Service Providers:')
        for sp in service_providers:
            print(f'ID: {sp.sp_id}, Name: {sp.name}, Email: {sp.user.email}, Phone: {sp.user.phone}')

        # Set choices for f_sp_id with ID, name, and email for clarity
        self.fields['f_sp_id'].queryset = service_providers
        self.fields['f_sp_id'].label_from_instance = lambda obj: f'ID: {obj.sp_id}, Name: {obj.name} - Email: {obj.user.email}'

class ServiceAdmin(admin.ModelAdmin):
    form = ServiceForm
    list_display = ('name', 'get_Service_provider')

    def get_Service_provider(self, obj):
        if obj.f_sp_id:
            return f'ID: {obj.f_sp_id.sp_id}, Name: {obj.f_sp_id.name} - Email: {obj.f_sp_id.user.email}'
        return 'No Service Provider'
    get_Service_provider.short_description = 'Service Provider'

admin.site.register(Service, ServiceAdmin)

# admin.site.register(Order)

# logic to edit add accont manager <=> service provider from

class AccountManagerServiceForm(forms.ModelForm):
    class Meta:
        model = AccountManagerService
        fields = ['f_accm_id', 'f_servp_id', 'date_assigned']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fetch AccountManagers and ServiceProviders
        account_managers = AccountManager.objects.select_related('user').all()
        service_providers = ServiceProvider.objects.select_related('user').all()

        # Print the fetched AccountManager instances for debugging
        print('Account Managers:')
        for am in account_managers:
            user = am.user
            print(f'ID: {am.am_id}, Name: {user.username}, Email: {user.email}, Phone: {user.phone}')

        # Print the fetched ServiceProvider instances for debugging
        print('Service Providers:')
        for sp in service_providers:
            user = sp.user
            print(f'ID: {sp.sp_id}, Name: {user.username}, Email: {user.email}, Phone: {user.phone}')

        # Set choices for f_accm_id with Account Manager details
        self.fields['f_accm_id'].queryset = account_managers
        self.fields['f_accm_id'].label_from_instance = lambda obj: f'ID: {obj.am_id}, Name: {obj.name} - Email: {obj.user.email}'

        # Set choices for f_servp_id with Service Provider details
        self.fields['f_servp_id'].queryset = service_providers
        self.fields['f_servp_id'].label_from_instance = lambda obj: f'ID: {obj.sp_id}, Name: {obj.name} - Email: {obj.user.email}'

class AccountManagerServiceAdmin(admin.ModelAdmin):
    form = AccountManagerServiceForm
    list_display = ('get_am_username', 'get_servp_username', 'date_assigned')

    def get_am_username(self, obj):
        if obj.f_accm_id:
            return f'ID: {obj.f_accm_id.am_id}, Name: {obj.f_accm_id.name} - Email: {obj.f_accm_id.user.email}'
        return 'No Account Manager'
    get_am_username.short_description = 'Account Manager'

    def get_servp_username(self, obj):
        if obj.f_servp_id:
            return f'ID: {obj.f_servp_id.sp_id}, Name: {obj.f_servp_id.name} - Email: {obj.f_servp_id.user.email}'
        return 'No Service Provider'
    get_servp_username.short_description = 'Service Provider'

admin.site.register(AccountManagerService, AccountManagerServiceAdmin)

# admin.site.register(AccountManagerService)


# logic for service order

class ServiceOrderForm(forms.ModelForm):
    class Meta:
        model = ServiceOrder
        fields = ['f_order_id', 'f_sp_id', 'f_service_id', 'f_amc_id', 'f_job_id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

       
        orders = Order.objects.all()
        service_providers = ServiceProvider.objects.select_related('user').all()
        services = Service.objects.all()
        account_managers_customers = AccountManagerCustomer.objects.all()
        jobs = Job.objects.all()

      
        print('Orders:')
        for order in orders:
            print(f'ID: {order.order_id}')  

        print('Service Providers:')
        for sp in service_providers:
            user = sp.user
            print(f'ID: {sp.sp_id}, Name: {sp.name}, Email: {user.email}, Phone: {user.phone}')

        print('Services:')
        for service in services:
            print(f'ID: {service.service_id}, Name: {service.name}')

        print('Account Manager Customers:')
        for amc in account_managers_customers:
            print(f'ID: {amc.am_cust_id}, Customer Name: {amc.f_cus_id.user.username}, Account Manager Name: {amc.f_am_id.name}')

        print('Jobs:')
        for job in jobs:
            print(f'ID: {job.job_id}, Name: {job.job_name}')  

     
        self.fields['f_order_id'].queryset = orders
        self.fields['f_sp_id'].queryset = service_providers
        self.fields['f_service_id'].queryset = services
        self.fields['f_amc_id'].queryset = account_managers_customers
        self.fields['f_job_id'].queryset = jobs

      
        self.fields['f_order_id'].label_from_instance = lambda obj: f'Order ID: {obj.order_id}'  
        self.fields['f_sp_id'].label_from_instance = lambda obj: f'ID: {obj.sp_id}, Name: {obj.name} - Email: {obj.user.email}'
        self.fields['f_service_id'].label_from_instance = lambda obj: f'ID: {obj.service_id}, Name: {obj.name}'
        self.fields['f_amc_id'].label_from_instance = lambda obj: f'AMC ID: {obj.am_cust_id}, Customer: {obj.f_cus_id.user.username}, Manager: {obj.f_am_id.user.username}'
        self.fields['f_job_id'].label_from_instance = lambda obj: f'Job ID: {obj.job_id}, Name: {obj.job_name}'


class ServiceOrderAdmin(admin.ModelAdmin):
    form = ServiceOrderForm
    list_display = ('f_order_id', 'get_sp_name', 'get_service_name', 'get_amc_info', 'get_job_info')

    def get_sp_name(self, obj):
        return f'ID: {obj.f_sp_id.sp_id}, Name: {obj.f_sp_id.name} - Email: {obj.f_sp_id.user.email}' if obj.f_sp_id else 'No Service Provider'
    get_sp_name.short_description = 'Service Provider'

    def get_service_name(self, obj):
        return f'ID: {obj.f_service_id.service_id}, Name: {obj.f_service_id.name}' if obj.f_service_id else 'No Service'
    get_service_name.short_description = 'Service'

    def get_amc_info(self, obj):
        if obj.f_amc_id:
            amc = obj.f_amc_id  # Get the AccountManagerCustomer instance
            manager = amc.f_am_id  # AccountManager instance
            customer = amc.f_cus_id  # Customer instance
            
            # Print debug information to understand the structure
            print(f'AMC ID: {amc.am_cust_id}, Customer: {customer.user.username}, Manager: {manager.name}, Manager ID: {manager.am_id}')
            
            # Return formatted string with Manager ID and other details
            return f'AMC ID: {amc.am_cust_id}, Customer: {customer.user.username}, Manager: {manager.name}, Manager ID: {manager.am_id}'
        
        return 'No Account Manager Customer'

    def get_job_info(self, obj):
        return f'Job ID: {obj.f_job_id.job_id}, Name: {obj.f_job_id.job_name}' if obj.f_job_id else 'No Job'
    get_job_info.short_description = 'Job Info'

admin.site.register(ServiceOrder, ServiceOrderAdmin)


#logic for service order finish

# admin.site.register(ServiceOrder)

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['f_cust_id', 'date']  # Include the fields you want to display and edit

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fetch Customer instances for dropdown
        customers = Customer.objects.all()

        # Set choices for f_cust_id with additional information
        self.fields['f_cust_id'].queryset = customers
        self.fields['f_cust_id'].label_from_instance = lambda obj: f'{obj.cus_id} - {obj.user.username}'

        # Debugging: Print the queryset for debugging
        print('Customer queryset:', customers)
        for customer in customers:
            print(f'Customer ID: {customer.cus_id}, Username: {customer.user.username}, Email: {customer.user.email}, Phone: {customer.user.phone}')

class OrderAdmin(admin.ModelAdmin):
    print("order form")
    form = OrderForm
    list_display = ('order_id', 'date', 'get_customer_info')

    def get_customer_info(self, obj):
        if obj.f_cust_id:
            customer = obj.f_cust_id
            return f'Customer ID: {customer.cus_id}, Username: {customer.user.username}, Email: {customer.user.email}, Phone: {customer.user.phone}'
        return 'No Customer'
    get_customer_info.short_description = 'Customer Info'

admin.site.register(Order, OrderAdmin)

# admin.site.register(Job)


class JobAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = (
        'job_id', 'job_name', 'state', 'job_type', 'starting_date', 'end_date', 'completion_time'
    )

    # Add filters for the list view
    list_filter = ('state', 'job_type', 'starting_date', 'end_date')

    # Add search functionality
    search_fields = ('job_id', 'job_name')

    # Add ordering to the list view
    ordering = ('-starting_date',)

    # Add fieldsets for better organization on the detail view
    fieldsets = (
        (None, {
            'fields': ('job_id', 'job_name', 'state', 'job_type')
        }),
        ('Dates', {
            'fields': ('starting_date', 'end_date')
        }),
        ('Completion', {
            'fields': ('completion_time',)
        }),
    )

    # Add custom methods if needed
    def job_duration(self, obj):
        if obj.starting_date and obj.end_date:
            return (obj.end_date - obj.starting_date).days
        return None

    job_duration.short_description = 'Job Duration (days)'

# Register the Job model with the custom admin class
admin.site.register(Job, JobAdmin)

# admin.site.register(Report)

# class JobReportResultForm(forms.ModelForm):
#     class Meta:
#         model = JobReportResult
#         fields = ['report', 'total_jobs']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Add any custom form initialization here if needed



# @admin.register(JobReportResult)
# class JobReportResultAdmin(admin.ModelAdmin):
#     list_display = ('report', 'total_jobs_display')

#     def change_view(self, request, object_id, form_url='', extra_context=None):
#         self.current_user = request.user
#         return super().change_view(request, object_id, form_url, extra_context)

#     def total_jobs_display(self, obj):
#         if hasattr(self, 'current_user') and self.current_user.is_authenticated:
#             user_id = self.current_user.id
#             # Use the user_id to get data or perform actions
#             # Example usage:
#             total_jobs = calculate_job_stats('Q1', 2020, 'Q2', 2024, self.current_user)
#             return total_jobs
#         else:
#             return "User not logged in"

#     total_jobs_display.short_description = 'Total Jobs'


@admin.register(JobReportResult)
class JobReportResultAdmin(admin.ModelAdmin):
    list_display = ('report', 'total_jobs')
    list_filter = ('report',)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'quarter_from', 'year_from', 'quarter_to', 'year_to', 'created_at')
    list_filter = ('quarter_from', 'year_from', 'quarter_to', 'year_to')


admin.site.register(OrderReportResult)
admin.site.register(UserStatistics)
admin.site.register(JobStatistics)


