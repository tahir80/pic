# python manage.py analyze_orders <account_manager_username> <customer_username>

from django.conf import settings
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db.models import Sum
from pic.models import Order, ServiceOrder, AccountManager, Customer, AccountManagerCustomer
from pic.stat_analysis.models import OrderReportResult, Report
from django.db import models
import datetime

class Command(BaseCommand):
    help = 'Calculate order statistics for a specific customer and store them in OrderReportResult'

    def add_arguments(self, parser):
        parser.add_argument('account_manager_username', type=str, help='Username of the Account Manager')
        parser.add_argument('customer_username', type=str, help='Username of the Customer')

    def handle(self, *args, **options):
        account_manager_username = options['account_manager_username']
        customer_username = options['customer_username']

        User = apps.get_model(settings.AUTH_USER_MODEL)

        # Fetch the user instances
        try:
            account_manager_user = User.objects.get(username=account_manager_username)
            customer_user = User.objects.get(username=customer_username)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR('One or both of the specified users do not exist.'))
            return

        # Check if AccountManager is linked with Customer
        if not self.is_linked(account_manager_user, customer_user):
            self.stderr.write(self.style.ERROR('The specified Account Manager is not linked with the Customer.'))
            return

        # Perform the analysis
        total_orders, total_revenue, average_order_value = self.calculate_order_statistics(customer_user)

        # Get the overall date range from the dataset
        date_range = self.get_date_range(customer_user)

        # Create the report
        report = Report.objects.create(
            title='Order Report',
            created_by=customer_user,
            quarter_from=date_range['quarter_from'],
            year_from=date_range['year_from'],
            quarter_to=date_range['quarter_to'],
            year_to=date_range['year_to'],
        )

        # Create or update the OrderReportResult
        order_report_result, created = OrderReportResult.objects.get_or_create(
            report=report,
            defaults={
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'average_order_value': average_order_value,
            }
        )

        if not created:
            order_report_result.total_orders = total_orders
            order_report_result.total_revenue = total_revenue
            order_report_result.average_order_value = average_order_value
            order_report_result.save()

        self.stdout.write(self.style.SUCCESS(f'Total Orders: {total_orders}'))
        self.stdout.write(self.style.SUCCESS(f'Total Revenue: ${total_revenue:.2f}'))
        self.stdout.write(self.style.SUCCESS(f'Average Order Value: ${average_order_value:.2f}'))

    def is_linked(self, account_manager_user, customer_user):
        try:
            account_manager = AccountManager.objects.get(user=account_manager_user)
            customer = Customer.objects.get(user=customer_user)
            return AccountManagerCustomer.objects.filter(f_am_id=account_manager, f_cus_id=customer).exists()
        except (AccountManager.DoesNotExist, Customer.DoesNotExist):
            return False

    def calculate_order_statistics(self, customer_user):
        # Fetch the customer instance
        try:
            customer = Customer.objects.get(user=customer_user)
        except Customer.DoesNotExist:
            self.stderr.write(self.style.ERROR('The specified Customer does not exist.'))
            return 0, 0, 0

        # Filter orders for the specified customer using `cus_id`
        orders = Order.objects.filter(f_cust_id=customer.cus_id)  # Use cus_id

        # Total Orders
        total_orders = orders.count()

        # Total Revenue from Service Orders
        # Corrected field name for filtering ServiceOrders related to Orders
        total_revenue = ServiceOrder.objects.filter(f_order_id__in=orders).aggregate(Sum('price'))['price__sum'] or 0

        # Average Order Value
        average_order_value = total_revenue / total_orders if total_orders > 0 else 0

        return total_orders, total_revenue, average_order_value

    def get_date_range(self, customer_user):
        # Fetch the customer instance
        try:
            customer = Customer.objects.get(user=customer_user)
        except Customer.DoesNotExist:
            self.stderr.write(self.style.ERROR('The specified Customer does not exist.'))
            return {
                'quarter_from': 'Q1',
                'year_from': datetime.datetime.now().year,
                'quarter_to': 'Q1',
                'year_to': datetime.datetime.now().year,
            }

        # Filter orders for the specified customer using `cus_id`
        orders = Order.objects.filter(f_cust_id=customer.cus_id)  # Use cus_id

        # Get the earliest and latest dates from the orders
        min_date = orders.aggregate(min_date=models.Min('date'))['min_date']
        max_date = orders.aggregate(max_date=models.Max('date'))['max_date']

        if min_date and max_date:
            start_year = min_date.year
            start_quarter = self.get_quarter(min_date)
            end_year = max_date.year
            end_quarter = self.get_quarter(max_date)
        else:
            # Fallback if no dates are available
            start_year = end_year = datetime.datetime.now().year
            start_quarter = end_quarter = 'Q1'

        return {
            'quarter_from': start_quarter,
            'year_from': start_year,
            'quarter_to': end_quarter,
            'year_to': end_year,
        }

    def get_quarter(self, date):
        # Determine the quarter from a given date
        month = date.month
        if 1 <= month <= 3:
            return 'Q1'
        elif 4 <= month <= 6:
            return 'Q2'
        elif 7 <= month <= 9:
            return 'Q3'
        elif 10 <= month <= 12:
            return 'Q4'
        return 'Q1'
