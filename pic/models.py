from django.db import models

# Model for AccountManager
class AccountManager(models.Model):
    am_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        db_table = 'AccountManager'

    def __str__(self):
        return self.name


# Model for Customer
class Customer(models.Model):
    cus_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.EmailField()

    class Meta:
        db_table = 'Customer'

    def __str__(self):
        return self.name


# Model for Status
class Status(models.Model):
    status_id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=255)

    class Meta:
        db_table = 'Status'

    def __str__(self):
        return self.status


# Model for ServiceProvider
class ServiceProvider(models.Model):
    sp_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'Service_Provider'

    def __str__(self):
        return self.name


# Model for AccountManagerCustomer (Join table)
class AccountManagerCustomer(models.Model):
    am_cust_id = models.AutoField(primary_key=True)
    f_am_id = models.ForeignKey(AccountManager, on_delete=models.CASCADE, db_column='F_AM_ID')
    f_cus_id = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='F_CUS_ID')
    date_assigned = models.DateField()

    class Meta:
        db_table = 'AccountManagerCustomer'

    def __str__(self):
        return f'{self.f_am_id} - {self.f_cus_id}'


# Model for Service
class Service(models.Model):
    service_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    f_sp_id = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, db_column='F_SP_ID')

    class Meta:
        db_table = 'Service'

    def __str__(self):
        return self.name


# Model for Order
class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    date = models.DateField()
    f_cust_id = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='F_cust_ID')
    f_status_id = models.ForeignKey(Status, on_delete=models.CASCADE, db_column='F_Status_ID')

    class Meta:
        db_table = 'Order'

    def __str__(self):
        return f'Order {self.order_id}'



# Model for AccountManagerService (Join table)
class AccountManagerService(models.Model):
    ams_id = models.AutoField(primary_key=True)
    f_accm_id = models.ForeignKey(AccountManager, on_delete=models.CASCADE, db_column='F_AccM_ID')
    f_servp_id = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, db_column='F_ServP_ID')
    date_assigned = models.DateField()

    class Meta:
        db_table = 'AccountManagerService'

    def __str__(self):
        return f'{self.f_accm_id} - {self.f_servp_id}'


# Model for Job
class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('regular', 'Regular'),
        ('wafer_run', 'Wafer Run'),
    ]
    STATE_CHOICES = [
        ('created', 'Created'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]

    job_id = models.AutoField(primary_key=True)
    job_name = models.CharField(max_length=200)
    state = models.CharField(max_length=100, choices=STATE_CHOICES)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    starting_date = models.DateField()
    end_date = models.DateField()
    completion_time = models.FloatField(help_text="Time in days which were spent to complete the job.")

    class Meta:
        db_table = 'Job'

    def __str__(self):
        return self.job_name
    

    # Model for ServiceOrder
class ServiceOrder(models.Model):
    so_id = models.AutoField(primary_key=True)
    f_order_id = models.ForeignKey(Order, on_delete=models.CASCADE, db_column='F_Order_ID')
    f_sp_id = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, db_column='F_SP_ID')
    f_service_id = models.ForeignKey(Service, on_delete=models.CASCADE, db_column='F_service_ID')
    f_amc_id = models.ForeignKey(AccountManagerCustomer, on_delete=models.CASCADE, db_column='F_AMC_ID')
    f_job_id = models.ForeignKey(Job, on_delete=models.CASCADE, db_column='F_job_ID')

    class Meta:
        db_table = 'Service_Order'

    def __str__(self):
        return f'Service Order {self.so_id}'
