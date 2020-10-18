import os
from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("User must have an username")
        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_propic_image_path(instance, filename):
    print(instance)
    # print(filename)
    # new_filename = random.randint(1, 9999999999)
    new_filename = datetime.now()
    name, ext = get_filename_ext(filename)
    name = name[:5]
    print('file upload')
    final_filename = '{name}-{new_filename}{ext}'.format(new_filename=new_filename, ext=ext, name=name)
    print(new_filename)
    print('-----------------------')
    print(final_filename)
    print('-----------------------')
    print(name)
    print('-----------------------')

    print(ext, 'ext', filename, 'filename', instance)
    return 'images/users/' + str(instance) + '/profilePic/{final_filename}'.format(final_filename=final_filename)


class accountUsers(AbstractBaseUser):
    email = models.EmailField(verbose_name='email', max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last_login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    pro_pic = models.ImageField(upload_to=upload_propic_image_path, null=True, blank=True)
    user_address = models.CharField(null=True, max_length=255, blank=True)
    user_dob = models.DateField(null=True, max_length=255)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

# Create your models here.
