import uuid
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db.utils import IntegrityError
from pic.models import (AccountManager, Customer, ServiceProvider, Order, 
                        Service, ServiceOrder, AccountManagerCustomer, AccountManagerService)
from pic.execution.models import Job
from pic.stat_analysis.models.report import Report
from pic.stat_analysis.models.statistics import JobReportResult, JobCompletionTime, JobStatusCount
import datetime
import random
from django.core.exceptions import ValidationError

User = get_user_model()

class CombinedTestCase(TestCase):
    def setUp(self):
        # Create Account Manager
        self.account_manager_user = User.objects.create_user(
            username=f'account_manager_{random.randint(1000, 9999)}',
            password='password',
            user_type=1
        )
        self.account_manager = AccountManager.objects.create(
            user=self.account_manager_user,
            name='Account Manager 1'
        )

        # Create Customer
        self.customer_user = User.objects.create_user(
            username=f'customer_{random.randint(1000, 9999)}',
            password='password',
            user_type=2
        )
        self.customer = Customer.objects.create(
            user=self.customer_user,
            name='Customer 1',
            phone='1234567890',
            email='customer1@example.com'
        )

        # Link Account Manager with Customer
        self.account_manager_customer = AccountManagerCustomer.objects.create(
            f_am_id=self.account_manager,
            f_cus_id=self.customer,
            date_assigned='2024-01-01'
        )

        # Create Service Providers
        self.linked_sp = ServiceProvider.objects.create(
            user=User.objects.create_user(
                username=f'sp_linked_{random.randint(1000, 9999)}',
                password='password',
                user_type=3
            ),
            name='Service Provider Linked',
            phone='0987654321',
            email='sp_linked@example.com'
        )
        
        self.unlinked_sp = ServiceProvider.objects.create(
            user=User.objects.create_user(
                username=f'sp_unlinked_{random.randint(1000, 9999)}',
                password='password',
                user_type=3
            ),
            name='Service Provider Unlinked',
            phone='1122334455',
            email='sp_unlinked@example.com'
        )

        # Link Account Manager with the Service Provider
        AccountManagerService.objects.create(
            f_accm_id=self.account_manager,
            f_servp_id=self.linked_sp,
            date_assigned='2024-01-01'
        )

        # Create Services
        self.linked_service = Service.objects.create(
            name='Linked Service',
            f_sp_id=self.linked_sp
        )
        
        self.unlinked_service = Service.objects.create(
            name='Unlinked Service',
            f_sp_id=self.unlinked_sp
        )

        # Create Order
        self.order = Order.objects.create(
            date='2024-01-01',
            f_cust_id=self.customer
        )

        # Create test jobs
        self.job1 = Job.objects.create(
            job_id='JOB001',
            job_name='Test Job 1',
            state='completed',
            job_type='regular',
            starting_date=datetime.datetime(2023, 1, 1),
            end_date=datetime.datetime(2023, 3, 31),
            completion_time=5.0
        )
        self.job2 = Job.objects.create(
            job_id='JOB002',
            job_name='Test Job 2',
            state='active',
            job_type='wafer_run',
            starting_date=datetime.datetime(2023, 4, 1),
            end_date=datetime.datetime(2023, 6, 30),
            completion_time=7.0
        )

        # Clear any existing ServiceOrders to ensure clean state
        ServiceOrder.objects.all().delete()

    def test_customer_can_only_order_from_linked_service_providers(self):
        print("Starting test: Customer can only order from linked service providers.")

        # Create a valid Service Order with a linked Service Provider
        print("Creating a service order with a linked service provider...")
        ServiceOrder.objects.create(
            f_order_id=self.order,
            f_sp_id=self.linked_sp,
            f_service_id=self.linked_service,
            f_amc_id=self.account_manager_customer,
            f_job_id=self.job1,
            price=100.00
        )
        print("Service order with linked service provider created successfully.")

        # Attempt to create a Service Order with an unlinked Service Provider
        print("Attempting to create a service order with an unlinked service provider...")
        try:
            ServiceOrder.objects.create(
                f_order_id=self.order,
                f_sp_id=self.unlinked_sp,
                f_service_id=self.unlinked_service,
                f_amc_id=self.account_manager_customer,
                f_job_id=self.job1,
                price=100.00
            )
        except ValidationError as e:
            # Expected behavior: validation error due to constraint
            print(f'ValidationError caught as expected: {e}')
        except Exception as e:
            # Fail the test if any other unexpected exception occurs
            self.fail(f'Unexpected exception raised: {e}')
        else:
            # Fail the test if no exception occurs
            self.fail('ValidationError was not raised for an unlinked service provider.')

        # Verify the linked service order count
        print("Verifying the number of service orders for the linked service provider...")
        linked_service_orders = ServiceOrder.objects.filter(f_sp_id=self.linked_sp)
        linked_count = linked_service_orders.count()
        print(f"Number of service orders for the linked service provider: {linked_count}")
        self.assertEqual(linked_count, 1, "There should be exactly one service order for the linked service provider.")
        
        # Verify the unlinked service order attempt was not successful
        print("Verifying the number of service orders for the unlinked service provider...")
        unlinked_service_orders = ServiceOrder.objects.filter(f_sp_id=self.unlinked_sp)
        unlinked_count = unlinked_service_orders.count()
        print(f"Number of service orders for the unlinked service provider: {unlinked_count}")
        self.assertEqual(unlinked_count, 0, "Service orders should not be created for unlinked service providers.")

        print("Test completed: Customer can only order from linked service providers.")

    def test_get_job_stats(self):
        call_command('get_job_stats', 'Q1', 2023, 'Q2', 2023, username=self.account_manager_user.username)
        print('Ran `get_job_stats` command.')

        # Check that a report was created
        try:
            report = Report.objects.get(
                quarter_from='Q1',
                year_from=2023,
                quarter_to='Q2',
                year_to=2023
            )
            print(f'Found Report: {report}')
        except Report.DoesNotExist:
            self.fail('Report was not created.')

        job_stats = JobReportResult.objects.get(report=report)
        print(f'Found JobReportResult: {job_stats}')

        # Assertions
        self.assertEqual(job_stats.total_jobs, 2, 'Total jobs reported does not match expected value.')

    def test_detailed_statistics(self):
        call_command('get_job_stats', 'Q1', 2023, 'Q2', 2023, username=self.account_manager_user.username)
        print('Ran `get_job_stats` command.')

        # Check that detailed statistics were created
        try:
            report = Report.objects.get(
                quarter_from='Q1',
                year_from=2023,
                quarter_to='Q2',
                year_to=2023
            )
            print(f'Found Report: {report}')
        except Report.DoesNotExist:
            self.fail('Report was not created.')

        avg_completion_times = JobCompletionTime.objects.filter(report=report)
        status_counts = JobStatusCount.objects.filter(report=report)
        print(f'Found JobCompletionTimes: {avg_completion_times}')
        print(f'Found JobStatusCounts: {status_counts}')

        # Assertions
        self.assertEqual(avg_completion_times.count(), 2, 'Number of average completion times does not match expected value.')
        self.assertEqual(status_counts.count(), 2, 'Number of status counts does not match expected value.')

        # Check the specific values
        type1_avg = avg_completion_times.get(job_type='regular')
        type2_avg = avg_completion_times.get(job_type='wafer_run')
        self.assertEqual(type1_avg.average_completion_time, 5.0, 'Average completion time for regular jobs does not match expected value.')
        self.assertEqual(type2_avg.average_completion_time, 7.0, 'Average completion time for wafer run jobs does not match expected value.')

        completed_status = status_counts.get(status='completed')
        active_status = status_counts.get(status='active')
        self.assertEqual(completed_status.count, 1, 'Count of completed jobs does not match expected value.')
        self.assertEqual(active_status.count, 1, 'Count of active jobs does not match expected value.')
