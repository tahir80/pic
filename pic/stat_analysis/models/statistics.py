"""stat_analysis.models.statistics.py

"""
from django.db import models

from .report import Report


class JobReportResult(models.Model):
    """Model to store analysis results for the Jobs.

    `Job` model is defined in `execution` app.
    """
    report = models.OneToOneField(Report, on_delete=models.CASCADE)

    total_jobs = models.IntegerField()


class OrderReportResult(models.Model):
    """Model to store analysis results for the customer Orders.

    Note: `Order` model should be defined in Task 1.
    """
    report = models.OneToOneField(Report, on_delete=models.CASCADE)

    # Example data fields of what the order report may contain.
    total_orders = models.IntegerField()
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2)


# class JobStatistics(models.Model):
#     """Model to store detailed job statistics."""

#     report = models.OneToOneField(Report, on_delete=models.CASCADE)


#     average_job_completion_time_per_job_type = models.JSONField(default=dict)
#     number_of_jobs_per_status = models.JSONField(default=dict)

#     def __str__(self):
#         return f"Job Statistics for {self.report}"


class JobCompletionTime(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    job_type = models.CharField(max_length=20, choices=[
        ('regular', 'Regular'),
        ('wafer_run', 'Wafer Run'),
    ])
    average_completion_time = models.FloatField(help_text="Average completion time in days.")

    class Meta:
        unique_together = ('report', 'job_type')

    def __str__(self):
        return f"{self.job_type}: {self.average_completion_time} days"

class JobStatusCount(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=[
        ('created', 'Created'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ])
    count = models.IntegerField()

    class Meta:
        unique_together = ('report', 'status')

    def __str__(self):
        return f"{self.status}: {self.count}"

