from django.shortcuts import redirect
from django.utils.timezone import now

class BasicMembershipMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            user_membership = getattr(request.user, 'usermembership', None)
            if user_membership:
                if user_membership.membership.name == 'basic' and not user_membership.is_active():
                    return redirect('request_upgrade')  # Redirect to upgrade page
        return self.get_response(request)
