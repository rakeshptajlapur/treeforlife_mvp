from .models import Corporate

def corporate_context_processor(request):
    """
    Adds 'is_corporate_admin' to all template contexts
    if the user has a corporate account.
    """
    if request.user.is_authenticated:
        try:
            request.user.corporate_account
            return {'is_corporate_admin': True}
        except Corporate.DoesNotExist:
            return {'is_corporate_admin': False}
    return {'is_corporate_admin': False}


