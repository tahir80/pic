# Task 1: Database Schema in Django

For this task, I designed a database schema in `models.py` and other folders (stat_analysis, execution) to meet the specified requirements. The schema is visualized in the following diagram:

![Database Schema](https://github.com/tahir80/pic/blob/main/my_project_models_updated.png)

## Requirements and Implementation

### Requirement 1: Account Management
**Objective:** An account manager registers new customer accounts.

**Implementation:**
- Created `AccountManager` and `Customer` tables.
- Linked these tables to the `User` model.
- Added an associative entity `AccountManagerCustomer` to manage the relationships between account managers and customers.

### Requirement 2: Order Creation and Visibility
**Objective:** Customers create orders, which should be visible to their account managers.

**Implementation:**
- Implemented `Order` and `ServiceOrder` tables to manage customer orders and associated services.

### Requirement 3: Service Ordering Constraints
**Objective:** Customers can only add services from service providers managed by their account manager.

**Implementation:**
- Created the `AccountManagerService` table to link account managers with service providers.
- Added logic to the `ServiceOrder` table to ensure that customers can only place orders with service providers managed by their account manager. The validation logic is as follows:

```python
def clean(self):
    # Retrieve account manager, service provider, and customer
    account_manager = self.f_amc_id.f_am_id  # AccountManager
    service_provider = self.f_sp_id  # ServiceProvider
    customer = self.f_amc_id.f_cus_id  # Customer
    
    # Validate that the AccountManager is linked to the Customer
    if not AccountManagerCustomer.objects.filter(
        f_am_id=account_manager,
        f_cus_id=customer
    ).exists():
        raise ValidationError("The account manager is not linked to the customer.")

    # Validate that the ServiceProvider is managed by the AccountManager
    if not AccountManagerService.objects.filter(
        f_accm_id=account_manager,
        f_servp_id=service_provider
    ).exists():
        raise ValidationError("The service provider is not managed by the account manager.")
    
def save(self, *args, **kwargs):
    self.clean()  # Ensure validation is called
    super().save(*args, **kwargs)

````
# Task 2: Enhancing Analysis Capabilities, Reporting, and Unit Tests

## Requirement # 1

Expand the job statistics to include:
1. Average job completion time per job type.
2. Number of jobs per status.

## Solution

I implemented this functionality in the `pic/management/commands/get_job_stats.py` script. This script calculates and stores job statistics by:
1. Taking user input for the reporting period and username.
2. Retrieving and validating the user.
3. Computing various metrics such as total job counts, average job completion times, and job status counts.

To execute the script and generate the statistics, use the following command:

```bash
python manage.py get_job_stats Q1 2021 Q2 2023 --username=tahir
```
## Related Models

``` python
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
```

## Requirement # 2



