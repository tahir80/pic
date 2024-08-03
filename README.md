# Task 1: Database Schema in Django

My first task was to create a database schema in models.py that captures the requirements listed in task 1.

![alt text]()


### Requirement 1: An account manager registers the new user account for this customer.

1. for this requirement to fullfil, I created account manager and customer tables and link it to the User type.
2. I also created associatitive entity to make sure that account managers are linked with customers (AccountmanagerCustomer)

### Requirement 2: The customer creates an order. The complete order is visible to the account manager

1. I created an Order and ServiceOrder tables to capture this scenario.

### Requirement 3: The customer fills the order with services from the service providers. However, there’s a limitation: she can add services only from those service providers which are managed by her account manager.

1. I implemented this scenario by ensuring that Acccount managers and Service providers are linked together using AccountmanagerService table.
2. Seconfly, I implemend logic in the ServiceOrder Table to ensure that only customer who are linked with Account managers can place their orders from the registerd Service providers. Please see details here:

```python 
def clean(self):
        # Get the account manager, service provider, and customer
        account_manager = self.f_amc_id.f_am_id  # AccountManager
        service_provider = self.f_sp_id  # ServiceProvider
        customer = self.f_amc_id.f_cus_id  # Customer
        
        # Check if the AccountManager is linked to the Customer
        if not AccountManagerCustomer.objects.filter(
            f_am_id=account_manager,
            f_cus_id=customer
        ).exists():
            raise ValidationError("The account manager is not linked to the customer.")

        # Check if the ServiceProvider is managed by the AccountManager
        if not AccountManagerService.objects.filter(
            f_accm_id=account_manager,
            f_servp_id=service_provider
        ).exists():
            raise ValidationError("The service provider is not managed by the account manager.")
    def save(self, *args, **kwargs):
        self.clean()  # Ensure validation is called
        super().save(*args, **kwargs)
```



