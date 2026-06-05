# employees/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.utils import timezone

from payroll.payroll_service import settings

class HR(SoftDeletableModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    hr_id = models.CharField(max_length=10, unique=True)
    contact = models.CharField(max_length=15)

    def __str__(self):
        return self.user.username

class SalaryJobType(models.Model):
    job_type = models.CharField(max_length=50, unique=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    deduction_money = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.job_type

class Employee(SoftDeletableModel):
    JOB_TYPE_CHOICES = [
        ('Senior Developer', 'Senior Developer'),
        ('Junior Developer', 'Junior Developer'),
        ('Manager', 'Manager'),
        ('Clerk', 'Clerk'),
        ('tester','tester')

    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=10, unique=True)
    hr = models.ForeignKey(HR, on_delete=models.SET_NULL, null=True)
    contact = models.CharField(max_length=15)
    status = models.CharField(max_length=10, default='inactive')
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES)

    def __str__(self):
        return self.user.username




class LeaveManager(models.Manager):
    def total_leave_days_for_employee(self, employee):
        today = timezone.localdate()
        start_of_month = today.replace(day=1)
        end_of_month = (start_of_month + timedelta(days=31)).replace(day=1) - timedelta(days=1)

        leave_days = self.filter(employee=employee, status='Approved', start_date__lte=end_of_month, end_date__gte=start_of_month).annotate(
            duration=models.ExpressionWrapper(
                models.F('end_date') - models.F('start_date') + timedelta(days=1),
                output_field=models.DurationField()
            )
        ).aggregate(total_days=models.Sum('duration'))
        return leave_days['total_days'].days if leave_days['total_days'] else 0

    def calculate_payroll(self, employee, total_leave_days):
        job_type = employee.job_type
        salary_job_type = SalaryJobType.objects.get(job_type=job_type)

        total_salary = salary_job_type.salary
        deduction_amount = total_leave_days * salary_job_type.deduction_money
        net_salary = total_salary - deduction_amount

        # Get the first day of the current month
        month_start = timezone.localdate().replace(day=1)
        # Get the last day of the current month
        month_end = (month_start + timedelta(days=31)).replace(day=1) - timedelta(days=1)

        # Check if there is already a Payroll record for this employee for the current month
        payroll, created = Payroll.objects.update_or_create(
            employee=employee,
            month__year=month_start.year,
            month__month=month_start.month,
            defaults={
                'total_salary': total_salary,
                'deduction_amount': deduction_amount,
                'net_salary': net_salary,
                'payment_date': timezone.localdate()
            }
        )
        return payroll




class Leave(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, default='pending')

    objects = LeaveManager()

    def __str__(self):
        return f"{self.employee.name} - {self.status}"
    
class Payroll(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    total_salary = models.DecimalField(max_digits=10, decimal_places=2)
    deduction_amount = models.DecimalField(max_digits=10, decimal_places=2)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField(default=timezone.now)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee.name} - {self.month.strftime('%B %Y')}"

from django.db import models
from django.utils import timezone

class TimeEntry(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='time_entries')
    date = models.DateField()
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # e.g. 8.5
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(HR, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.employee.name} - {self.date} ({self.hours_worked}h)"
    
    # any roll user roll can be related to one or more companies, and each company can have multiple users with different roles. 
    # This allows for a flexible and scalable system where users can have different permissions and access levels based on their role within the company.
    
    # models.py (create a new app called "core" or put in employees)

class Company(SoftDeletableModel):
    name = models.CharField(max_length=200)
    legal_name = models.CharField(max_length=200, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)  # EIN for Florida
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class UserRole(models.TextChoices):
    OWNER = 'owner', 'Company Owner'
    HR = 'hr', 'HR Manager'
    EMPLOYEE = 'employee', 'Employee'


class UserCompany(models.Model):
    """This is the key table for multi-company support"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=UserRole.choices)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'company')
        # Example: One user can't be Owner and Employee in same company

    def __str__(self):
        return f"{self.user} - {self.company} ({self.role})"
    
    ## SOFT DELETE: Instead of deleting records, we can set is_active=False. This way we keep historical data and can reactivate if needed.


class SoftDeletableModel(models.Model):
    """
    Base model for Soft Delete functionality
    """
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deleted_%(class)s'
    )

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, **kwargs):
        """Override delete to do soft delete"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = kwargs.get('deleted_by', None)  # Pass user who deleted
        self.save()

    def hard_delete(self):
        """Real permanent delete"""
        super().delete()
    