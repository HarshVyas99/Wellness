import datetime
from django import template

register = template.Library()


@register.simple_tag
def conversation_with(conversation,user_id):
    return conversation.participants.exclude(id=user_id).first().username 

@register.filter
def doctor_conversation_user_id(conversation,doctor_id):
    return conversation.participants.exclude(id=doctor_id).first().id

@register.filter
def is_doctor(user):
    return user.groups.filter(name='Doctors').exists()

@register.filter
def is_admin(user):
    return user.groups.filter(name='Admins').exists()