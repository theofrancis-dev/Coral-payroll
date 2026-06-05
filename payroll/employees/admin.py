from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Employee, HR, Leave, SalaryJobType

admin.site.register(Employee)
admin.site.register(HR)
admin.site.register(Leave)
admin.site.register(SalaryJobType)