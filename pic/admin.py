from django.contrib import admin
from pic.execution.models import Job
# Register your models here.
from django.contrib import admin
from pic.stat_analysis.models.report import Report
# from pic.stat_analysis.models.statistics import JobReportResult, OrderReportResult, JobStatistics
from pic.stat_analysis.models.statistics import JobReportResult, OrderReportResult, JobStatusCount, JobCompletionTime
from pic.stat_analysis.stat_utils import calculate_job_stats
from django.http import HttpResponse
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from pic.models import User, AccountManager, Customer, ServiceProvider, AccountManagerCustomer, Service, Order, AccountManagerService, ServiceOrder
from django import forms

from django.db.models import Avg, Count, Sum


# REPORT LAB
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO


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

class ServiceOrderForm(forms.ModelForm):
    class Meta:
        model = ServiceOrder
        fields = ['f_order_id', 'f_sp_id', 'f_service_id', 'f_amc_id', 'f_job_id', 'price']

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
    list_display = ('f_order_id', 'get_sp_name', 'get_service_name', 'get_amc_info', 'get_job_info', 'get_price')

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


    def get_price(self, obj):
        return f'${obj.price:.2f}' if obj.price else 'No Price'
    get_price.short_description = 'Price'

admin.site.register(ServiceOrder, ServiceOrderAdmin)


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

@admin.register(JobReportResult)
class JobReportResultAdmin(admin.ModelAdmin):
    # Define the fields to be displayed in the list view
    list_display = (
        'report_title', 
        # 'total_jobs', 
        'total_jobs_display'
    )
    
    # Define the filters available in the admin interface
    list_filter = (
        'report',  # Filter by the report associated with the result
    )
    

    search_fields = ('report__title',)  # Allows searching by report title

    # Add ordering to the list view
    ordering = ('-total_jobs',)  # Order by total jobs in descending order

    # Custom method to display the report title
    def report_title(self, obj):
        return obj.report.title if obj.report else 'No Report'
    report_title.short_description = 'Report Title'

    # Custom method to display the total jobs with formatting
    def total_jobs_display(self, obj):
        return f'{obj.total_jobs:,}'  # Formats the total jobs with commas
    total_jobs_display.short_description = 'Total Jobs'


class OrderReportResultForm(forms.ModelForm):
    class Meta:
        model = OrderReportResult
        fields = ['report', 'total_orders', 'total_revenue', 'average_order_value']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
       


class OrderReportResultAdmin(admin.ModelAdmin):
    # Optionally use a custom form
    form = OrderReportResultForm

    # Fields to display in the list view
    list_display = ('report', 'total_orders', 'total_revenue', 'average_order_value')

    # Add filters if needed (e.g., filter by `report`)
    list_filter = ('report',)

    # Add search functionality (if needed, though it may not be necessary for integer and decimal fields)
    search_fields = ('report__title',)  # Searching by related report's title

    # Optional: Add ordering to the list view
    ordering = ('-total_revenue',)

    # Optional: Add custom methods if needed
    def total_orders_display(self, obj):
        return obj.total_orders
    total_orders_display.short_description = 'Total Orders'

    def total_revenue_display(self, obj):
        return f'${obj.total_revenue:.2f}'
    total_revenue_display.short_description = 'Total Revenue'

    def average_order_value_display(self, obj):
        return f'${obj.average_order_value:.2f}'
    average_order_value_display.short_description = 'Average Order Value'

admin.site.register(OrderReportResult, OrderReportResultAdmin)


class JobCompletionTimeInline(admin.TabularInline):
    model = JobCompletionTime
    extra = 1
    fields = ('job_type', 'average_completion_time')
    readonly_fields = ('average_completion_time',)

class JobStatusCountInline(admin.TabularInline):
    model = JobStatusCount
    extra = 1
    fields = ('status', 'count')
    readonly_fields = ('count',)

class JobReportResultInline(admin.StackedInline):
    model = JobReportResult
    extra = 1
    fields = ('total_jobs',)
    readonly_fields = ('total_jobs',)

class OrderReportResultInline(admin.StackedInline):
    model = OrderReportResult
    extra = 1
    fields = ('total_orders', 'total_revenue', 'average_order_value')
    readonly_fields = ('total_revenue', 'average_order_value')


# PDF export function
def export_to_pdf(modeladmin, request, queryset):
    buffer = BytesIO()

    # Set up the PDF document with landscape orientation
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),  # Use landscape mode
        rightMargin=inch*0.75,
        leftMargin=inch*0.75,
        topMargin=inch*0.75,
        bottomMargin=inch*0.75
    )

    elements = []

    # Prepare header information for each report
    styles = getSampleStyleSheet()
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        alignment=1,  # Center alignment
    )

    for report in queryset:
        # Prepare header information
        header_info = [
            f"Created By: {report.created_by.username}",
            f"Created At: {report.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Year From: {report.year_from}",
            f"Year To: {report.year_to}",
            f"Quarter From: {report.quarter_from}",
            f"Quarter To: {report.quarter_to}"
        ]
        
        # Add header information to elements
        for info in header_info:
            p = Paragraph(info, header_style)
            elements.append(p)
        
        elements.append(Spacer(1, 12))  # Add some space between the header and the table

        # Prepare data for PDF
        data = [
            [Paragraph("Title", header_style), Paragraph("Total Jobs", header_style), 
             Paragraph("Total Orders", header_style), Paragraph("Total Revenue", header_style),
             Paragraph("Avg Order Value", header_style), 
             Paragraph("Avg Comp Time Regular", header_style), 
             Paragraph("Avg Comp Time Wafer Run", header_style), 
             Paragraph("Jobs Created", header_style), 
             Paragraph("Jobs Active", header_style), 
             Paragraph("Jobs Completed", header_style)]
        ]
        
        for report in queryset:
            total_jobs = report.jobreportresult.total_jobs if hasattr(report, 'jobreportresult') else 'N/A'
            total_orders = report.orderreportresult.total_orders if hasattr(report, 'orderreportresult') else 'N/A'
            total_revenue = report.orderreportresult.total_revenue if hasattr(report, 'orderreportresult') else 'N/A'
            average_order_value = report.orderreportresult.average_order_value if hasattr(report, 'orderreportresult') else 'N/A'
            
            try:
                average_completion_time_regular = report.jobcompletiontime_set.get(job_type='regular').average_completion_time
            except JobCompletionTime.DoesNotExist:
                average_completion_time_regular = 'N/A'
            
            try:
                average_completion_time_wafer_run = report.jobcompletiontime_set.get(job_type='wafer_run').average_completion_time
            except JobCompletionTime.DoesNotExist:
                average_completion_time_wafer_run = 'N/A'
            
            try:
                jobs_created = report.jobstatuscount_set.get(status='created').count
            except JobStatusCount.DoesNotExist:
                jobs_created = 'N/A'
            
            try:
                jobs_active = report.jobstatuscount_set.get(status='active').count
            except JobStatusCount.DoesNotExist:
                jobs_active = 'N/A'
            
            try:
                jobs_completed = report.jobstatuscount_set.get(status='completed').count
            except JobStatusCount.DoesNotExist:
                jobs_completed = 'N/A'
            
            data.append([
                report.title, total_jobs, total_orders, total_revenue, average_order_value, 
                average_completion_time_regular, average_completion_time_wafer_run, 
                jobs_created, jobs_active, jobs_completed
            ])
    
        # Create and style the table
        col_widths = [1.1*inch]*len(data[0])  # Adjust column widths as needed
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ]))
        elements.append(table)
        
        # Add space between each report section if printing multiple
        elements.append(Spacer(1, 24))

    # Build PDF document
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reports.pdf"'
    return response

export_to_pdf.short_description = "Export selected reports to PDF"

class ReportAdmin(admin.ModelAdmin):
    inlines = [
        JobCompletionTimeInline,
        JobStatusCountInline,
        JobReportResultInline,
        OrderReportResultInline,
    ]
    
    list_display = (
        'title', 'created_at', 'created_by',
        'quarter_from', 'year_from', 'quarter_to', 'year_to',
        'total_jobs', 'total_orders', 'total_revenue', 'average_order_value',
        'average_completion_time_regular', 'average_completion_time_wafer_run',
        'jobs_created', 'jobs_active', 'jobs_completed'
    )

    def total_jobs(self, obj):
        return obj.jobreportresult.total_jobs if hasattr(obj, 'jobreportresult') else 'N/A'
    total_jobs.admin_order_field = 'jobreportresult__total_jobs'

    def total_orders(self, obj):
        return obj.orderreportresult.total_orders if hasattr(obj, 'orderreportresult') else 'N/A'
    total_orders.admin_order_field = 'orderreportresult__total_orders'

    def total_revenue(self, obj):
        return obj.orderreportresult.total_revenue if hasattr(obj, 'orderreportresult') else 'N/A'
    total_revenue.admin_order_field = 'orderreportresult__total_revenue'

    def average_order_value(self, obj):
        return obj.orderreportresult.average_order_value if hasattr(obj, 'orderreportresult') else 'N/A'
    average_order_value.admin_order_field = 'orderreportresult__average_order_value'

    def average_completion_time_regular(self, obj):
        try:
            return obj.jobcompletiontime_set.get(job_type='regular').average_completion_time
        except JobCompletionTime.DoesNotExist:
            return 'N/A'
    average_completion_time_regular.admin_order_field = 'jobcompletiontime__average_completion_time'

    def average_completion_time_wafer_run(self, obj):
        try:
            return obj.jobcompletiontime_set.get(job_type='wafer_run').average_completion_time
        except JobCompletionTime.DoesNotExist:
            return 'N/A'
    average_completion_time_wafer_run.admin_order_field = 'jobcompletiontime__average_completion_time'

    def jobs_created(self, obj):
        try:
            return obj.jobstatuscount_set.get(status='created').count
        except JobStatusCount.DoesNotExist:
            return 'N/A'
    jobs_created.admin_order_field = 'jobstatuscount__count'

    def jobs_active(self, obj):
        try:
            return obj.jobstatuscount_set.get(status='active').count
        except JobStatusCount.DoesNotExist:
            return 'N/A'
    jobs_active.admin_order_field = 'jobstatuscount__count'

    def jobs_completed(self, obj):
        try:
            return obj.jobstatuscount_set.get(status='completed').count
        except JobStatusCount.DoesNotExist:
            return 'N/A'
    jobs_completed.admin_order_field = 'jobstatuscount__count'

    search_fields = ('title', 'created_by__username')
    list_filter = ('created_by', 'quarter_from', 'year_from', 'quarter_to', 'year_to')
    actions = [export_to_pdf]

admin.site.register(Report, ReportAdmin)

class JobCompletionTimeAdmin(admin.ModelAdmin):
    list_display = ('report', 'job_type', 'average_completion_time')
    list_filter = ('job_type', 'report')
    search_fields = ('report__title', 'job_type')

class JobStatusCountAdmin(admin.ModelAdmin):
    list_display = ('report', 'status', 'count')
    list_filter = ('status', 'report')
    search_fields = ('report__title', 'status')

# Register the models with the admin site
admin.site.register(JobCompletionTime, JobCompletionTimeAdmin)
admin.site.register(JobStatusCount, JobStatusCountAdmin)
