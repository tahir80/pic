from django.db import models
from pic.execution.models import Job
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        (1, 'AccountManager'),
        (2, 'Customer'),
        (3, 'ServiceProvider'),
    )

    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=1)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name_plural = "PIC's Users"




# Model for AccountManager
class AccountManager(models.Model):
    am_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'user_type': 1}, default=1)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        db_table = 'AccountManager'
        verbose_name_plural = "Account Managers list"

    def __str__(self):
        return self.name


# Model for Customer
class Customer(models.Model):
    cus_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'user_type': 2})

    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.EmailField()

    class Meta:
        db_table = 'Customer'
        verbose_name_plural = "Customers list"

    def __str__(self):
        return self.name


# Model for Status
# class Status(models.Model):

#      STATUS_TYPES = [
#         ('pending', 'Pending'),
#         ('Shipped', 'Wafer Run'),
#     ]
#     status_id = models.AutoField(primary_key=True)
#     status = models.CharField(max_length=255)

#     class Meta:
#         db_table = 'Status'

#     def __str__(self):
#         return self.status


# Model for ServiceProvider
class ServiceProvider(models.Model):
    sp_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'user_type': 3})
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.EmailField()

    class Meta:
        db_table = 'Service_Provider'
        verbose_name_plural = "Sevice Providers list"

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
    # f_status_id = models.ForeignKey(Status, on_delete=models.CASCADE, db_column='F_Status_ID')

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



    # Model for ServiceOrder
class ServiceOrder(models.Model):
    so_id = models.AutoField(primary_key=True)
    f_order_id = models.ForeignKey(Order, on_delete=models.CASCADE, db_column='F_Order_ID')
    f_sp_id = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, db_column='F_SP_ID')
    f_service_id = models.ForeignKey(Service, on_delete=models.CASCADE, db_column='F_service_ID')
    f_amc_id = models.ForeignKey(AccountManagerCustomer, on_delete=models.CASCADE, db_column='F_AMC_ID')
    f_job_id = models.ForeignKey(Job, on_delete=models.CASCADE, db_column='F_job_ID')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    class Meta:
        db_table = 'Service_Order'

    def __str__(self):
        return f'Service Order {self.so_id}'



class UserStatistics(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_orders = models.IntegerField(default=0)
    total_services_used = models.IntegerField(default=0)
    total_jobs_completed = models.IntegerField(default=0)

    class Meta:
        db_table = 'UserStatistics'
        verbose_name_plural = "User Statistics"

    def __str__(self):
        return f'Statistics for {self.user.username}'
    

    

@receiver(post_save, sender=User)
def create_role_specific_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 1:  # Account Manager
            AccountManager.objects.create(user=instance)
        elif instance.user_type == 2:  # Customer
            Customer.objects.create(user=instance)
        elif instance.user_type == 3:  # Service Provider
            ServiceProvider.objects.create(user=instance)
