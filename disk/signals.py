from pathlib import Path
from shutil import rmtree

from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.contrib.auth.models import User

from httpagentparser import simple_detect

from disk.models import GenericFile, RecycleFile, AuthLog, Profile, Role, RoleLimit
from disk.utils import get_secret_path


# First user creation and related root directory creation
@receiver(post_save, sender=User, dispatch_uid="post_save_user")
def post_save_user(sender, instance, created, **kwargs):
    if created:
        role = Role.objects.get_or_create(role_key='common', defaults={'role_name': 'general user'})[0]
        Profile.objects.create(user=instance, role=role)
        root = get_secret_path(instance.username.encode())
        GenericFile.objects.create(create_by=instance, file_name=root, file_path=root)
        RecycleFile.objects.create(create_by=instance, origin_path=root, recycle_path=root)
        Path(settings.PAN_ROOT / root).mkdir(parents=True)
        Path(settings.BIN_ROOT / root).mkdir(parents=True)


# Delete file data and delete source file
@receiver(pre_delete, sender=GenericFile, dispatch_uid="pre_delete_file")
def pre_delete_file(sender, instance, **kwargs):
    if instance.folder is None:
        raise PermissionError('forbidden')
    path = settings.PAN_ROOT / instance.file_path
    if path.exists():
        if instance.file_type is None:
            rmtree(path)
        else:
            path.unlink()


# Delete recovered file data and delete source file
@receiver(pre_delete, sender=RecycleFile, dispatch_uid="pre_delete_refile")
def pre_delete_refile(sender, instance, **kwargs):
    if instance.origin.folder is None:
        raise PermissionError('forbidden')
    path = settings.BIN_ROOT / instance.recycle_path
    if path.exists():
        if instance.origin.file_type is None:
            rmtree(path)
        else:
            path.unlink()


# user log
@receiver(user_logged_in, dispatch_uid='user_logged_in')
def logged_in_log(sender, request, user, **kwargs):
    # save root directory
    root = user.files.get(folder=None)
    rec_root = user.recycle_files.get(origin=None)
    request.session['root'] = str(root.file_uuid)
    request.session['rec_root'] = str(rec_root.pk)
    # save current user limit and storage space
    queryset = RoleLimit.objects.select_related('limit').filter(role=user.profile.role)
    terms = {'used': root.file_size}
    for item in queryset:
        terms[item.limit.limit_key] = item.value

    request.session['terms'] = terms

    ip = request.META.get('REMOTE_ADDR')
    ua = simple_detect(request.headers.get('user-agent'))
    AuthLog.objects.create(username=user.username, ipaddress=ip, os=ua[0], browser=ua[1], action='0')


@receiver(user_logged_out, dispatch_uid='user_logged_out')
def logged_out_log(sender, request, user, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    ua = simple_detect(request.headers.get('user-agent'))
    AuthLog.objects.create(username=user.username, ipaddress=ip, os=ua[0], browser=ua[1], action='1')


@receiver(user_login_failed, dispatch_uid='user_login_failed')
def login_failed_log(sender, credentials, request, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    ua = simple_detect(request.headers.get('user-agent'))
    AuthLog.objects.create(username=credentials.get('username'), ipaddress=ip, os=ua[0], browser=ua[1], action='2')
