from pathlib import Path
from shutil import move

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User

from pan.utils import get_uuid, get_unique_filename


# 删除被关联字段后获取的填充值
def get_deleted_role():
    return Role.objects.get_or_create(role_key='anonymous', defaults={'role_name': 'anonymous'})[0]


def get_deleted_user():
    return User.objects.get_or_create(username='anonymous', defaults={'password': 'anonymous'})[0]


def get_deleted_file():
    return GenericFile.objects.get_or_create(
        file_name='anonymous',
        create_by=None,
        defaults={
            'file_uuid': get_uuid(),
            'file_size': 0,
            'is_del': True,
        }
    )[0]


def get_deleted_file_type():
    return FileType.objects.get_or_create(
        suffix='',
        defaults={'type_name': 'unknown'}
    )[0]


def get_deleted_file_share():
    return FileShare.objects.get_or_create(
        secret_key='anonymous',
        defaults={
            'signature': 'anonymous',
            'file': get_deleted_file(),
            'expire_time': timezone.now()
        }
    )[0]


# 代理管理器
class MessageManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(action='0')


class ApplyManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(action='1')


class BaseModel(models.Model):
    """基础模型"""

    create_time = models.DateTimeField(auto_now_add=True, verbose_name='create time')
    update_time = models.DateTimeField(auto_now=True, verbose_name='update time')
    create_by = models.ForeignKey(User, on_delete=models.SET(get_deleted_user), null=True, blank=True,
                                  verbose_name='creator')
    update_by = models.ForeignKey(User, on_delete=models.SET(get_deleted_user), null=True, blank=True,
                                  related_name='+', verbose_name='updater')
    remark = models.TextField(blank=True, verbose_name='remark')

    class Meta:
        abstract = True


class Role(BaseModel):
    """role"""

    role_name = models.CharField(max_length=50, verbose_name='role name')
    role_key = models.CharField(unique=True, max_length=50, verbose_name='role character')

    class Meta:
        verbose_name = 'role'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.role_name


class Limit(BaseModel):
    """限制"""

    limit_name = models.CharField(max_length=50, verbose_name='restriction name')
    limit_key = models.CharField(unique=True, max_length=50, verbose_name='restricted characters')

    class Meta:
        verbose_name = 'limit'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.limit_name


class RoleLimit(BaseModel):
    """role限制"""

    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name='role')
    limit = models.ForeignKey(Limit, on_delete=models.CASCADE, verbose_name='limit')
    value = models.BigIntegerField(default=0, verbose_name='value')

    class Meta:
        verbose_name = 'role limit'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'role：{self.role.role_name}，limit：{self.limit.limit_name}'


class Notice(BaseModel):
    """通知"""

    title = models.CharField(max_length=50, verbose_name='title')
    content = models.TextField(verbose_name='notification content')

    class Meta:
        verbose_name = 'notify'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Profile(BaseModel):
    """user profile"""

    GENDER = [
        ('0', '女'),
        ('1', '男')
    ]

    create_by = None

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='user')
    avatar = models.ImageField(upload_to=get_unique_filename, default='default/user.svg', verbose_name='avatar')
    gender = models.CharField(max_length=1, choices=GENDER, blank=True, verbose_name='gender')
    role = models.ForeignKey(Role, on_delete=models.SET(get_deleted_role), verbose_name='role')

    class Meta:
        verbose_name = 'user profile'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.username


class FileType(BaseModel):
    """文件类型"""

    type_name = models.CharField(max_length=50, verbose_name='type name')
    suffix = models.CharField(unique=True, blank=True, max_length=10, verbose_name='file extension')

    class Meta:
        verbose_name = "file type"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.suffix


class GenericFile(BaseModel):
    """文件(文件夹)"""

    create_by = models.ForeignKey(User, on_delete=models.SET(get_deleted_user), related_name='files',
                                  null=True, blank=True, verbose_name='creator')

    file_name = models.CharField(max_length=100, verbose_name='file name')
    file_uuid = models.UUIDField(unique=True, default=get_uuid, verbose_name='file no')
    file_type = models.ForeignKey(FileType, on_delete=models.SET(get_deleted_file_type), related_name='files',
                                  null=True, blank=True, verbose_name="file type")
    file_size = models.BigIntegerField(default=0, verbose_name='file size(byte)')
    file_path = models.CharField(db_index=True, max_length=500, verbose_name="file path")
    folder = models.ForeignKey('self', on_delete=models.CASCADE, to_field='file_uuid', related_name='files',
                               null=True, blank=True, verbose_name="file parent")
    is_del = models.BooleanField(default=False, verbose_name='recycling')

    class Meta:
        verbose_name = 'file'
        verbose_name_plural = verbose_name

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._loaded_values = dict(zip(field_names, values))
        return instance

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """
        定制save方法，文件更新传播
        """
        super().save(force_insert, force_update, using, update_fields)
        if hasattr(self, '_loaded_values'):
            objs = []

            def recursive_update(obj, parent):
                obj.file_path = Path(parent.file_path) / obj.file_name
                objs.append(obj)
                if obj.file_type is None:
                    for sub in GenericFile.objects.filter(folder=obj):
                        recursive_update(sub, obj)

            if self.folder_id != self._loaded_values['folder_id']:
                folders = []
                dst = self.folder
                src = GenericFile.objects.get(file_uuid=self._loaded_values['folder_id'])

                move(str(settings.PAN_ROOT / self.file_path), str(settings.PAN_ROOT / dst.file_path))

                while dst.folder:
                    dst.file_size += self.file_size
                    folders.append(dst)
                    dst = dst.folder
                while src.folder:
                    src.file_size -= self.file_size
                    folders.append(src)
                    src = src.folder

                recursive_update(self, self.folder)
                GenericFile.objects.bulk_update(folders, ('file_size',))

            if self.file_name != self._loaded_values['file_name']:
                Path(settings.PAN_ROOT / self.file_path).rename(
                    settings.PAN_ROOT / self.folder.file_path / self.file_name
                )
                recursive_update(self, self.folder)

            if objs:
                GenericFile.objects.bulk_update(objs, ('file_path',))

    def __str__(self):
        return self.file_name


class RecycleFile(BaseModel):
    """recycling files"""

    create_by = models.ForeignKey(User, on_delete=models.SET(get_deleted_user), related_name='recycle_files',
                                  null=True, blank=True, verbose_name='creator')
    recycle_path = models.CharField(max_length=500, verbose_name="recycling path")
    origin_path = models.CharField(max_length=500, verbose_name="original path")
    origin = models.OneToOneField(GenericFile, on_delete=models.CASCADE, to_field='file_uuid',
                                  related_name='recycle_file', null=True, blank=True, verbose_name="source file")

    class Meta:
        verbose_name = 'recycling files'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.origin.file_name if self.origin else '-'


class FileShare(BaseModel):
    """文件分享记录"""

    secret_key = models.CharField(db_index=True, max_length=10, verbose_name='share key')
    signature = models.CharField(max_length=70, verbose_name='digital signature')
    file = models.ForeignKey(GenericFile, on_delete=models.CASCADE, to_field='file_uuid', verbose_name='file')
    expire_time = models.DateTimeField(verbose_name='expiration')
    summary = models.CharField(blank=True, max_length=100, verbose_name='share additional description')

    class Meta:
        verbose_name = 'file sharing'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.file.file_name


class AcceptRecord(BaseModel):
    """文件接收记录"""

    create_by = models.ForeignKey(User, on_delete=models.SET(get_deleted_user), related_name='accept_records',
                                  null=True, blank=True, verbose_name='receiver')

    file_share = models.ForeignKey(FileShare, on_delete=models.SET(get_deleted_file_share), verbose_name='file sharing')
    anonymous = models.GenericIPAddressField(null=True, blank=True, verbose_name='anonymous user')

    class Meta:
        verbose_name = 'document receiving record'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.create_by.username if self.create_by else self.anonymous


class Letter(BaseModel):
    """留言和申请"""

    ACTIONS = [
        ('0', 'message'),
        ('1', 'apply')
    ]

    STATUS = [
        ('0', 'unapproved'),
        ('1', 'pass'),
        ('2', 'not pass')
    ]

    create_by = models.ForeignKey(User, on_delete=models.SET(get_deleted_user), related_name='letters',
                                  null=True, blank=True, verbose_name='creator')

    action = models.CharField(max_length=1, choices=ACTIONS, verbose_name='type')
    status = models.CharField(max_length=1, default='0', choices=STATUS, verbose_name='status')
    content = models.TextField(verbose_name='content')

    class Meta:
        verbose_name = 'message and apply'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.get_action_display()


class Message(Letter):
    """留言代理"""
    objects = MessageManager()

    class Meta:
        proxy = True
        verbose_name = 'message'
        verbose_name_plural = verbose_name


class Apply(Letter):
    """审核代理"""
    objects = ApplyManager()

    class Meta:
        proxy = True
        verbose_name = 'apply'
        verbose_name_plural = verbose_name


class AuthLog(models.Model):
    """用户验证日志"""

    ACTIONS = [
        ('0', 'log in'),
        ('1', 'log out'),
        ('2', 'log filed')
    ]

    username = models.CharField(max_length=128, verbose_name='user name')
    ipaddress = models.GenericIPAddressField(verbose_name='ip address')
    browser = models.CharField(max_length=200, verbose_name='browser')
    os = models.CharField(max_length=30, verbose_name='operating system')
    action = models.CharField(max_length=1, choices=ACTIONS, verbose_name='action')
    msg = models.CharField(max_length=100, verbose_name='message')
    auth_time = models.DateTimeField(auto_now_add=True, verbose_name='time')

    class Meta:
        verbose_name = 'User authentication log'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
