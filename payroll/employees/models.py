from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


# ====================== SOFT DELETE ======================
class SoftDeletableModel(models.Model):
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
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = kwargs.get('deleted_by', None)
        self.save()

    def hard_delete(self):
        super().delete()


class SoftDeletableManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


# ====================== CORE MODELS ======================
class Department(SoftDeletableModel):
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('company', 'name')
        ordering = ['name']

    def __str__(self):
        return self.name


class JobPosition(SoftDeletableModel):
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='job_positions')
    
    title = models.CharField(max_length=150)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_hourly = models.BooleanField(default=True)
    flsa_status = models.CharField(
        max_length=20,
        choices=[('exempt', 'Exempt'), ('non_exempt', 'Non-Exempt')],
        default='non_exempt'
    )
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('company', 'title')
        ordering = ['title']

    def __str__(self):
        return self.title


class Company(SoftDeletableModel):
    name = models.CharField(max_length=200)
    legal_name = models.CharField(max_length=200, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)   # EIN
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class UserCompany(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[
        ('owner', 'Company Owner'),
        ('hr', 'HR Manager'),
        ('employee', 'Employee')
    ])
    is_active = models.BooleanField(default=True)
    date_joined = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'company')

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.company} ({self.role})"


# ====================== HR & EMPLOYEE ======================
class HR(SoftDeletableModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='hrs')  # Important for multi-company
    name = models.CharField(max_length=100)
    hr_id = models.CharField(max_length=20, unique=True)
    contact = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name


class Employee(SoftDeletableModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees')
    
    name = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=20, unique=True)
    hr = models.ForeignKey(HR, on_delete=models.SET_NULL, null=True, blank=True)
    contact = models.CharField(max_length=20, blank=True)
    
    job_position = models.ForeignKey(
        JobPosition, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='employees'
    )
    
    status = models.CharField(max_length=20, default='active', choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave')
    ])

    def __str__(self):
        return self.name


# ====================== TIME & LEAVE ======================
class TimeEntry(SoftDeletableModel):
    STATUS_CHOICES = [('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='time_entries')
    date = models.DateField()
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, default=0)
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


class Leave(SoftDeletableModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ])

    def __str__(self):
        return f"{self.employee.name} - {self.start_date} to {self.end_date}"


# ====================== PAYROLL ======================
class Payroll(SoftDeletableModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payrolls')
    total_salary = models.DecimalField(max_digits=12, decimal_places=2)
    deduction_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2)
    month = models.DateField()   # First day of the month
    payment_status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid')
    ])
    payment_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('employee', 'month')

    def __str__(self):
        return f"{self.employee.name} - {self.month.strftime('%B %Y')}"