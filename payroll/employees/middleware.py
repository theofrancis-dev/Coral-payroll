from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect

from payroll.employees.models import Company, UserCompany

class CompanyMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated:
            return

        # Get company from session
        company_id = request.session.get('current_company_id')
        
        if company_id:
            try:
                request.current_company = Company.objects.get(id=company_id)
                request.current_user_company = UserCompany.objects.get(
                    user=request.user, company=request.current_company
                )
            except:
                request.current_company = None
        else:
            # Auto-select first company if user has only one
            user_companies = UserCompany.objects.filter(user=request.user, is_active=True)
            if user_companies.count() == 1:
                request.session['current_company_id'] = user_companies.first().company_id
                request.current_company = user_companies.first().company