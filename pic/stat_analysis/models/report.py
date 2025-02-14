"""stat_analysis.models.report.py

"""
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings 


class Report(models.Model):
    # metadata
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Reference the user model via settings.AUTH_USER_MODEL
        on_delete=models.CASCADE,
        related_name='reports_created'
    )

    # Report settings
    quarter_from = models.CharField(max_length=2)  # Q1, Q2, Q3, Q4
    year_from = models.IntegerField()
    quarter_to = models.CharField(max_length=2)  # Q1, Q2, Q3, Q4
    year_to = models.IntegerField()
