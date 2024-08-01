import datetime
from pic.execution.models import Job
from pic.stat_analysis.models.report import Report
from pic.stat_analysis.models.statistics import JobReportResult

def calculate_job_stats(quarter_from, year_from, quarter_to, year_to, user):
    """Calculate statistics for Job model for a given period."""

    start_date_from, end_date_from = get_quarter_dates(quarter_from, year_from)
    start_date_to, end_date_to = get_quarter_dates(quarter_to, year_to)

    start_date = min(start_date_from, start_date_to)
    end_date = max(end_date_from, end_date_to)

    # Count jobs within the date range
    total_jobs = Job.objects.filter(
        starting_date__gte=start_date,
        end_date__lte=end_date
    ).count()


    print(f"Total jobs counted: {total_jobs}")

    # Get or create a Report instance
    report, created = Report.objects.get_or_create(
        quarter_from=quarter_from,
        year_from=year_from,
        quarter_to=quarter_to,
        year_to=year_to,
        defaults={
            'title': 'Job Report',
            'created_at': datetime.datetime.now(),
            'created_by': user,  # Set created_by to the actual user
        }
    )

    # Get or create a JobReportResult instance
    job_stats, created = JobReportResult.objects.get_or_create(
        report=report,
        defaults={'total_jobs': total_jobs}
    )

    # Update the total_jobs if the instance already existed
    if not created:
        job_stats.total_jobs = total_jobs
        job_stats.save()

    return job_stats

def get_quarter_dates(quarter, year):
    """Return the start and end dates for a given quarter and year."""
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
