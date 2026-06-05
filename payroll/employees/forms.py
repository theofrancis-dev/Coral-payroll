from django import forms
from django.contrib.auth.models import User
from .models import Employee, HR, Leave,SalaryJobType

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        widgets = {
            'password': forms.PasswordInput(),
        }

class HRForm(forms.ModelForm):
    class Meta:
        model = HR
        fields = ['name', 'hr_id', 'contact']

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'employee_id', 'contact', 'job_type', 'hr']

class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['start_date', 'end_date', 'reason']

class SalaryJobTypeForm(forms.ModelForm):
    class Meta:
        model = SalaryJobType
        fields = ['job_type', 'salary', 'deduction_money']

class PayrollForm(forms.Form):
    # employee = forms.ModelChoiceField(queryset=Employee.objects.all()) # load all employees at once, which can be inefficient if there are many employees. Instead, we can load employees based on the HR's selection.
    employee = forms.ModelChoiceField(queryset=Employee.objects.none())  # Load employees based on HR selection dinamically