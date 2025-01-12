from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
from .models import MembershipPlan, UserMembership

@receiver(post_save, sender=User)
def assign_basic_membership(sender, instance, created, **kwargs):
    if created:  # Only for new users
        try:
            basic_plan = MembershipPlan.objects.get(name='basic')
            UserMembership.objects.create(
                user=instance,
                membership=basic_plan,
                start_date=now(),
                end_date=now() + timedelta(minutes=basic_plan.duration_minutes)
            )
        except MembershipPlan.DoesNotExist:
            print("Basic Membership plan is not set up in the database.")
