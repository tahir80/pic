
# Run this script usiing: python manage.py get_total_jobs Q1 2021 Q2 2023 --username=<username>
# Replace the values with yours!

from django.conf import settings
from django.core.management.base import BaseCommand
from django.apps import apps
from pic.execution.models import Job
from pic.stat_analysis.models import JobReportResult, Report
import datetime

class Command(BaseCommand):
    help = 'Calculate job statistics for a given period'

    def add_arguments(self, parser):
        parser.add_argument('quarter_from', type=str)
        parser.add_argument('year_from', type=int)
        parser.add_argument('quarter_to', type=str)
        parser.add_argument('year_to', type=int)
        parser.add_argument('--username', type=str, help='Username of the user creating the report')

    def handle(self, *args, **options):
        quarter_from = options['quarter_from']
        year_from = options['year_from']
        quarter_to = options['quarter_to']
        year_to = options['year_to']
        username = options.get('username', 'system')

        # Import the custom user model
        User = apps.get_model(settings.AUTH_USER_MODEL)

        # Fetch the user instance
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'User with username "{username}" does not exist.'))
            return

        job_stats = self.calculate_job_stats(quarter_from, year_from, quarter_to, year_to, user)
        self.stdout.write(self.style.SUCCESS(f'Job stats calculated: {job_stats.total_jobs} jobs'))

    def calculate_job_stats(self, quarter_from, year_from, quarter_to, year_to, user):
        start_date_from, end_date_from = self.get_quarter_dates(quarter_from, year_from)
        start_date_to, end_date_to = self.get_quarter_dates(quarter_to, year_to)

        start_date = min(start_date_from, start_date_to)
        end_date = max(end_date_from, end_date_to)

        total_jobs = Job.objects.filter(
            starting_date__gte=start_date,
            end_date__lte=end_date
        ).count()

        report, created = Report.objects.get_or_create(
            quarter_from=quarter_from,
            year_from=year_from,
            quarter_to=quarter_to,
            year_to=year_to,
            defaults={
                'title': 'Job Report',
                'created_at': datetime.datetime.now(),
                'created_by': user,
            }
        )

        job_stats, created = JobReportResult.objects.get_or_create(
            report=report,
            defaults={'total_jobs': total_jobs}
        )

        if not created:
            job_stats.total_jobs = total_jobs
            job_stats.save()

        return job_stats

    def get_quarter_dates(self, quarter, year):
        if quarter == 'Q1':
            start_date = datetime.date(year, 1, 1)
            end_date = datetime.date(year, 3, 31)
        elif quarter == 'Q2':
            start_date = datetime.date(year, 4, 1)
            end_date = datetime.date(year, 6, 30)
        elif quarter == 'Q3':
            start_date = datetime.date(year, 7, 1)
            end_date = datetime.date(year, 9, 30)
        elif quarter == 'Q4':
            start_date = datetime.date(year, 10, 1)
            end_date = datetime.date(year, 12, 31)
        else:
            raise ValueError("Invalid quarter. Please use 'Q1', 'Q2', 'Q3', or 'Q4'.")
        return start_date, end_date
