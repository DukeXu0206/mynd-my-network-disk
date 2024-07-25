from django.contrib import admin, messages
from django.contrib.admin.models import LogEntry
from django.utils.translation import ngettext

from pan.utils import file_size_format
from pan.models import (Profile, Role, Limit, RoleLimit,
                        FileType, GenericFile, RecycleFile, FileShare, AcceptRecord,
                        Notice, Letter, Message, Apply, AuthLog)

@admin.action(description='Application approved')
def make_pass(modeladmin, request, queryset):
    role = Role.objects.get_or_create(role_key='member', defaults={'role_name': 'vip'})[0]
    profiles = [item.create_by.profile for item in queryset]
    rows = queryset.update(status='1', update_by=request.user)
    for profile in profiles:
        profile.role = role

    Profile.objects.bulk_update(profiles, ['role'])
    modeladmin.message_user(request, ngettext(
        'passed %(count)d application',
        'passed %(count)d applications',
        rows
    ) % {'count': rows}, messages.SUCCESS)

@admin.action(description='Rejection of application')
def make_not_pass(modeladmin, request, queryset):
    rows = queryset.update(status='2', update_by=request.user)
    modeladmin.message_user(request, ngettext(
        'rejected %(count)d application',
        'rejected %(count)d applications',
        rows
    ) % {'count': rows}, messages.SUCCESS)


