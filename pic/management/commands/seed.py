from django.core.management.base import BaseCommand
from django.utils import timezone
from pic.models import (
    User, AccountManager, Customer, ServiceProvider, Service, Order,
    AccountManagerCustomer, AccountManagerService, ServiceOrder
)
from pic.execution.models import Job
from pic.stat_analysis.models.report import Report
from pic.stat_analysis.models.statistics import JobReportResult, OrderReportResult
from django.db import IntegrityError
import random

class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **options):
        # self.stdout.write('Clearing existing data...')
        
        # Clear data
        # User.objects.all().delete()
        # AccountManager.objects.all().delete()
        # Customer.objects.all().delete()
        # ServiceProvider.objects.all().delete()
        # Service.objects.all().delete()
        # Order.objects.all().delete()
        # AccountManagerCustomer.objects.all().delete()
        # AccountManagerService.objects.all().delete()
        # ServiceOrder.objects.all().delete()
        # Job.objects.all().delete()
        # Report.objects.all().delete()
        # JobReportResult.objects.all().delete()
        # OrderReportResult.objects.all().delete()

        # self.stdout.write('Database cleared. Populating database with sample data...')

        users = []
        account_managers = []
        customers = []
        service_providers = []
        services = []
        orders = []
        jobs = []

        # Create 5 unique Users
        for i in range(1, 6):
            username = f'user{i}'
            email = f'user{i}@example.com'
            phone = f'123-456-78{i:02}'
            user_type = (i % 3) + 1  # Ensure roles are evenly distributed

            user = User.objects.create_user(
                username=username,
                password='password123',
                email=email,
                phone=phone,
                user_type=user_type
            )
            users.append(user)
            self.stdout.write(f'Created user: {username}')

        # Create corresponding roles
        for i, user in enumerate(users):
            if user.user_type == 1:
                am = AccountManager.objects.create(
                    user=user,
                    name=f'Account Manager {i + 1}',
                    phone=user.phone,
                    email=user.email
                )
                account_managers.append(am)
                self.stdout.write(f'Created AccountManager for user: {user.username}')
            elif user.user_type == 2:
                cust = Customer.objects.create(
                    user=user,
                    name=f'Customer {i + 1}',
                    phone=user.phone,
                    email=user.email
                )
                customers.append(cust)
                self.stdout.write(f'Created Customer for user: {user.username}')
            elif user.user_type == 3:
                sp = ServiceProvider.objects.create(
                    user=user,
                    name=f'Service Provider {i + 1}',
                    phone=user.phone,
                    email=user.email
                )
                service_providers.append(sp)
                self.stdout.write(f'Created ServiceProvider for user: {user.username}')

        # Create 5 Jobs
        for i in range(1, 6):
            job = Job.objects.create(
                job_id=f'JOB{i}',
                job_name=f'Job {i}',
                state=random.choice(['created', 'active', 'completed']),
                job_type=random.choice(['regular', 'wafer_run']),
                starting_date=timezone.now() - timezone.timedelta(days=random.randint(1, 10)),
                end_date=timezone.now() - timezone.timedelta(days=random.randint(0, 10)),
                completion_time=random.uniform(0.1, 5.0)
            )
            jobs.append(job)
            self.stdout.write(f'Created Job {i}')

        # Create 5 Services
        for i in range(1, 6):
            service = Service.objects.create(
                name=f'Service {i}',
                f_sp_id=service_providers[i-1]  # Ensure no conflict with existing data
            )
            services.append(service)
            self.stdout.write(f'Created Service {i}')

        # Create 5 Orders
        for i in range(1, 6):
            order = Order.objects.create(
                date=timezone.now() - timezone.timedelta(days=random.randint(1, 30)),
                f_cust_id=customers[i-1],  # Ensure no conflict with existing data
            )
            orders.append(order)
            self.stdout.write(f'Created Order {i}')

        # Create 5 AccountManagerCustomer records
        for i in range(1, 6):
            AccountManagerCustomer.objects.create(
                f_am_id=account_managers[i-1],  # Ensure no conflict with existing data
                f_cus_id=customers[i-1],  # Ensure no conflict with existing data
                date_assigned=timezone.now() - timezone.timedelta(days=random.randint(1, 30))
            )
            self.stdout.write(f'Created AccountManagerCustomer {i}')

        # Create 5 AccountManagerService records
        for i in range(1, 6):
            AccountManagerService.objects.create(
                f_accm_id=account_managers[i-1],  # Ensure no conflict with existing data
                f_servp_id=service_providers[i-1],  # Ensure no conflict with existing data
                date_assigned=timezone.now() - timezone.timedelta(days=random.randint(1, 30))
            )
            self.stdout.write(f'Created AccountManagerService {i}')

        # Create 5 ServiceOrder records
        for i in range(1, 6):
            ServiceOrder.objects.create(
                f_order_id=orders[i-1],  # Ensure no conflict with existing data
                f_sp_id=service_providers[i-1],  # Ensure no conflict with existing data
                f_service_id=services[i-1],  # Ensure no conflict with existing data
                f_amc_id=AccountManagerCustomer.objects.order_by('?').first(),  # Adjust according to your models
                f_job_id=jobs[i-1]  # Ensure no conflict with existing data
            )
            self.stdout.write(f'Created ServiceOrder {i}')

        # Create 3 Reports
        for i in range(1, 4):
            report = Report.objects.create(
                title=f'Report {i}',
                created_by=users[i % 5],  # Ensure no conflict with existing data
                quarter_from=f'Q{random.randint(1, 4)}',
                year_from=random.randint(2021, 2023),
                quarter_to=f'Q{random.randint(1, 4)}',
                year_to=random.randint(2021, 2023)
            )
            self.stdout.write(f'Created Report {i}')

            JobReportResult.objects.create(
                report=report,
                total_jobs=Job.objects.count()
            )
            self.stdout.write(f'Created JobReportResult for Report {i}')

            OrderReportResult.objects.create(
                report=report,
                total_orders=Order.objects.count(),
                total_revenue=random.uniform(1000, 5000),
                average_order_value=random.uniform(100, 500)
            )
            self.stdout.write(f'Created OrderReportResult for Report {i}')

        self.stdout.write('Database populated successfully with sample data.')
