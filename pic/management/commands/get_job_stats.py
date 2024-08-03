from django.conf import settings
from django.core.management.base import BaseCommand
from django.apps import apps
from pic.execution.models import Job
from pic.stat_analysis.models import JobReportResult, Report
from pic.stat_analysis.models.statistics import JobCompletionTime, JobStatusCount

import datetime
from django.db.models import Avg, Count

class Command(BaseCommand):
    help = 'Calculate job statistics and detailed statistics for a given period'

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

        print(f"Handling command with the following parameters:")
        print(f"  From: {quarter_from} {year_from}")
        print(f"  To: {quarter_to} {year_to}")
        print(f"  Username: {username}")

        # Import the custom user model
        User = apps.get_model(settings.AUTH_USER_MODEL)

        # Fetch the user instance
        try:
            user = User.objects.get(username=username)
            print(f"User {username} found.")
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'User with username "{username}" does not exist.'))
            print(f"User {username} does not exist.")
            return

        # Calculate job stats and detailed statistics
        print("Calculating job statistics...")
        report = self.calculate_job_stats(quarter_from, year_from, quarter_to, year_to, user)
        print("Calculating detailed statistics...")
        self.calculate_detailed_statistics(report, quarter_from, year_from, quarter_to, year_to)

        self.stdout.write(self.style.SUCCESS(f'Statistics calculated and saved.'))
        print("Statistics calculated and saved.")

    def calculate_job_stats(self, quarter_from, year_from, quarter_to, year_to, user):
        start_date_from, end_date_from = self.get_quarter_dates(quarter_from, year_from)
        start_date_to, end_date_to = self.get_quarter_dates(quarter_to, year_to)

        start_date = min(start_date_from, start_date_to)
        end_date = max(end_date_from, end_date_to)

        print(f"Calculating total jobs from {start_date} to {end_date}...")
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

        if created:
            print(f"Created new report: {report}")
        else:
            print(f"Report already exists: {report}")

        job_stats, created = JobReportResult.objects.get_or_create(
            report=report,
            defaults={'total_jobs': total_jobs}
        )

        if not created:
            job_stats.total_jobs = total_jobs
            job_stats.save()
            print(f"Updated job stats: {job_stats}")
        else:
            print(f"Created job stats: {job_stats}")

        return report

    def calculate_detailed_statistics(self, report, quarter_from, year_from, quarter_to, year_to):
        start_date_from, end_date_from = self.get_quarter_dates(quarter_from, year_from)
        start_date_to, end_date_to = self.get_quarter_dates(quarter_to, year_to)

        start_date = min(start_date_from, start_date_to)
        end_date = max(end_date_from, end_date_to)

        # Calculate average completion time per job type
        print(f"Calculating average completion time from {start_date} to {end_date}...")
        avg_completion_time_per_job_type = Job.objects.filter(
            starting_date__gte=start_date,
            end_date__lte=end_date
        ).values('job_type').annotate(
            avg_completion_time=Avg('completion_time')
        ).order_by()

        for item in avg_completion_time_per_job_type:
            JobCompletionTime.objects.update_or_create(
                report=report,
                job_type=item['job_type'],
                defaults={'average_completion_time': item['avg_completion_time']}
            )
            print(f"Updated or created JobCompletionTime for {item['job_type']} with average completion time {item['avg_completion_time']}.")

        # Calculate number of jobs per status
        print(f"Calculating number of jobs per status from {start_date} to {end_date}...")
        num_jobs_per_status = Job.objects.filter(
            starting_date__gte=start_date,
            end_date__lte=end_date
        ).values('state').annotate(
            num_jobs=Count('id')
        ).order_by()

        for item in num_jobs_per_status:
            JobStatusCount.objects.update_or_create(
                report=report,
                status=item['state'],
                defaults={'count': item['num_jobs']}
            )
            print(f"Updated or created JobStatusCount for status {item['state']} with count {item['num_jobs']}.")

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
