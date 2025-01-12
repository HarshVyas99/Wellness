from django.shortcuts import redirect
from django.utils.timezone import now
from django.urls import resolve

class BasicMembershipMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            user_membership = getattr(request.user, 'usermembership', None)
            if user_membership:
                if user_membership.membership.name == 'basic' and not user_membership.is_active():
                    # Exclude 'profile' URL or any other URLs from the check
                    current_url_name = resolve(request.path_info).url_name
                    if current_url_name not in ['profile','request_upgrade','logout']:  # Avoid infinite redirect loop
                        return redirect('profile')  # Redirect to profile page
        return self.get_response(request)
