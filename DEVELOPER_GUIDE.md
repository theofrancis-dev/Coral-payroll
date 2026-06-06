soft delete

class Employee(SoftDeletableModel):
    ...
    objects = models.Manager()           # Shows everything (for audits)
    active = SoftDeletableManager()      # Default for normal use

How to Use ItNormal Delete (from views/admin):python

employee.delete(deleted_by=request.user)   # Soft delete

Show only active records:python

Employee.active.all()          # Only non-deleted
Employee.objects.all()         # Includes deleted (for audit)

Restore:python

employee.is_deleted = False
employee.deleted_at = None
employee.deleted_by = None
employee.save()

