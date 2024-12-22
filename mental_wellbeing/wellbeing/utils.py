from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta
from wellbeing.models import Conversation
from django.db.models import Count

def get_active_doctors():
    # Filter users in the 'Doctors' group who logged in within the last 15 minutes
    doctors_group = User.objects.filter(groups__name='Doctors')
    active_threshold = now() - timedelta(minutes=15)
    if doctors_group.filter(last_login__gte=active_threshold):
        return doctors_group.filter(last_login__gte=active_threshold)
    else:
        return doctors_group
    
from django.db.models import Q

def get_or_create_conversation(user_ids):
    """
    Ensures a conversation exists with the given participants.
    If it doesn't exist, creates a new one.

    Args:
        user_ids (list): List of user IDs to participate in the conversation.

    Returns:
        conversation (Conversation): The conversation object.
        created (bool): True if a new conversation was created, False otherwise.
    """
    # Ensure the user_ids are sorted to avoid duplicates due to ordering
    user_ids = sorted(user_ids)

    # Search for an existing conversation with the same participants
    conversations = Conversation.objects.filter(
        participants__id__in=user_ids
    ).annotate(num_participants=Count('participants')).filter(num_participants=len(user_ids))

    for conversation in conversations:
        if set(conversation.participants.values_list('id', flat=True)) == set(user_ids):
            return conversation, False  # Conversation already exists

    # If no conversation exists, create a new one
    conversation = Conversation.objects.create()
    conversation.participants.set(user_ids)  # Add participants
    return conversation, True

