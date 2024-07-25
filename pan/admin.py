from django.contrib import admin, messages
from django.contrib.admin.models import LogEntry
from django.utils.translation import ngettext

from pan.utils import file_size_format
from pan.models import (Profile, Role, Limit, RoleLimit,
                        FileType, GenericFile, RecycleFile, FileShare, AcceptRecord,
                        Notice, Letter, Message, Apply, AuthLog)


# admin base class
class BaseAdmin(admin.ModelAdmin):
    readonly_fields = ('create_by', 'create_time', 'update_by', 'update_time')
    list_per_page = 10

    def save_model(self, request, obj, form, change):
        if obj.create_by:
            obj.update_by = request.user
        else:
            obj.create_by = request.user
            obj.update_by = request.user
        super().save_model(request, obj, form, change)

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

# administrator log
@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['object_repr', 'object_id', 'action_flag', 'user', 'change_message']
    list_per_page = 12

@admin.register(Profile)
class ProfileAdmin(BaseAdmin):
    fieldsets = (
        (None, {
            'fields': ('user', 'avatar', 'gender', 'role')
        }),
        ('other information', {
            'fields': ('create_time', 'update_by', 'update_time', 'remark')
        })
    )
    autocomplete_fields = ('user',)
    search_fields = ('user__username',)
    list_select_related = ('user', 'role')
    list_display = ('user', 'role', 'gender')
    list_filter = ('gender', 'role')


@admin.register(Role)
class RoleAdmin(BaseAdmin):
    fieldsets = (
        (None, {
            'fields': ('role_name', 'role_key')
        }),
        ('other information', {
            'fields': ('create_by', 'create_time', 'update_by', 'update_time', 'remark')
        })
    )
    list_display = ('role_name', 'role_key')

@admin.register(Limit)
class LimitAdmin(BaseAdmin):
    fieldsets = (
        (None, {
            'fields': ('limit_name', 'limit_key')
        }),
        ('other information', {
            'fields': ('create_by', 'create_time', 'update_by', 'update_time', 'remark')
        })
    )
    list_display = ('limit_name', 'limit_key')

@admin.register(RoleLimit)
class RoleLimitAdmin(BaseAdmin):
    fieldsets = (
        (None, {
            'fields': ('role', 'limit', 'value', 'format_value')
        }),
        ('other information', {
            'fields': ('create_by', 'create_time', 'update_by', 'update_time', 'remark')
        })
    )
    list_select_related = ('role', 'limit')
    list_display = ('role', 'limit', 'format_value')
    list_filter = ('role', 'limit')

    @admin.display(description='Limit size')
    def format_value(self, obj):
        return file_size_format(obj.value)


@admin.register(FileType)
class FileTypeAdmin(BaseAdmin):
    fieldsets = (
        (None, {
            'fields': ('type_name', 'suffix')
        }),
        ('other information', {
            'fields': ('create_by', 'create_time', 'update_by', 'update_time', 'remark')
        })
    )
    search_fields = ('suffix',)
    list_display = ('type_name', 'suffix')


@admin.register(GenericFile)
class GenericFileAdmin(BaseAdmin):
    fieldsets = (
        (None, {
            'fields': ('file_uuid', 'file_name', 'format_type', 'format_size', 'folder', 'format_status')
        }),
        ('other information', {
            'fields': ('create_by', 'create_time', 'update_by', 'update_time', 'remark')
        })
    )
    search_fields = ('file_name', 'create_by__username')
    readonly_fields = BaseAdmin.readonly_fields + ('file_uuid', 'file_name', 'format_type', 'format_size', 'folder', 'format_status')
    list_select_related = ('create_by', 'file_type')
    list_display = ('file_name', 'format_type', 'format_size', 'format_status', 'create_by')
    list_filter = ('file_type', 'is_del')

    @admin.display(ordering='file_size', description='file size')
    def format_size(self, obj):
        return file_size_format(obj.file_size)

    @admin.display(description='file type')
    def format_type(self, obj):
        return obj.file_type.suffix if obj.file_type else 'folders'

    @admin.display(boolean=True, description='file status')
    def format_status(self, obj):
        return not obj.is_del

    def get_queryset(self, request):
        return super().get_queryset(request).exclude(folder=None)

    def has_add_permission(self, request):
        return False


@admin.register(RecycleFile)
class RecycleFileAdmin(BaseAdmin):
    fieldsets = (
        (None, {
            'fields': ('origin',)
        }),
        ('other information', {
            'fields': ('create_by', 'create_time', 'update_by', 'update_time', 'remark')
        })
    )
    search_fields = ('origin__file_name', 'create_by__username')
    list_select_related = ('origin', 'create_by')
    list_display = ('origin', 'create_by', 'create_time')

    def get_queryset(self, request):
        return super().get_queryset(request).exclude(origin=None)

    def has_add_permission(self, request):
        return False


@admin.register(FileShare)
class FileShareAdmin(BaseAdmin):
    fieldsets = (
        (None, {
            'fields': ('secret_key', 'signature', 'expire_time', 'file', 'summary')
        }),
        ('other information', {
            'fields': ('create_by', 'create_time', 'update_by', 'update_time', 'remark')
        })
    )
    search_fields = ('create_by__username', 'file__file_name')
    readonly_fields = BaseAdmin.readonly_fields + ('secret_key', 'signature', 'expire_time', 'file', 'summary')
    list_select_related = ('file',)
    list_display = ('file', 'create_time', 'expire_time')
    list_filter = ('file__file_type',)

    def has_add_permission(self, request):
        return False

@admin.register(AcceptRecord)
class AcceptRecordAdmin(BaseAdmin):
    fieldsets = (
        (None, {
            'fields': ('file_share', 'anonymous')
        }),
        ('other information', {
            'fields': ('create_by', 'create_time', 'update_by', 'update_time', 'remark')
        })
    )
    search_fields = ('create_by__username',)
    readonly_fields = BaseAdmin.readonly_fields + ('file_share', 'anonymous')
    list_select_related = ('file_share', 'create_by')
    list_display = ('file_share', 'create_by', 'anonymous')
    list_filter = ('file_share__file__file_type',)

    def has_add_permission(self, request):
        return False


@admin.register(Notice)
class NoticeAdmin(BaseAdmin):
    fieldsets = (
        (None, {
            'fields': ('title', 'content')
        }),
        ('other information', {
            'fields': ('create_by', 'create_time', 'update_by', 'update_time', 'remark')
        })
    )
    search_fields = ('create_by__username', 'title')
    list_select_related = ('create_by',)
    list_display = ('title', 'create_by')


@admin.register(Letter)
class LetterAdmin(admin.ModelAdmin):

    def has_module_permission(self, request):
        return False

    def get_model_perms(self, request):
        return {}


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('content',)
        }),
        ('other information', {
            'fields': ('create_by', 'create_time', 'update_by', 'update_time', 'remark')
        })
    )
    search_fields = ('create_by__username',)
    readonly_fields = ('content', 'create_by', 'create_time', 'update_by', 'update_time')
    list_select_related = ('create_by',)
    list_display = ('create_by', 'create_time')
    list_per_page = 10

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        obj.update_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Apply)
class ApplyAdmin(BaseAdmin):
    fieldsets = (
        (None, {
            'fields': ('status', 'content')
        }),
        ('other information', {
            'fields': ('create_by', 'create_time', 'update_by', 'update_time', 'remark')
        })
    )
    search_fields = ('create_by__username',)
    readonly_fields = BaseAdmin.readonly_fields + ('content',)
    actions = (make_pass, make_not_pass)
    list_select_related = ('create_by',)
    list_filter = ('status',)
    list_display = ('create_by', 'status', 'create_time')

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        obj.update_by = request.user
        super().save_model(request, obj, form, change)

        profile = obj.create_by.profile
        if obj.status == '1':
            profile.role = Role.objects.get_or_create(role_key='member', defaults={'role_name': 'vip'})[0]
            profile.save()
        else:
            profile.role = Role.objects.get_or_create(role_key='common', defaults={'role_name': 'general user'})[0]
            profile.save()


@admin.register(AuthLog)
class AuthLogAdmin(admin.ModelAdmin):
    fields = ('username', 'ipaddress', 'browser', 'os', 'action', 'auth_time', 'msg')
    search_fields = ('username',)
    readonly_fields = ('username', 'ipaddress', 'browser', 'os', 'action', 'auth_time')
    list_display = ('username', 'ipaddress', 'browser', 'os', 'action', 'auth_time')
    list_filter = ('action',)
    list_per_page = 15

    def has_add_permission(self, request):
        return False
