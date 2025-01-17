from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from .utils import *
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserAccountManager(BaseUserManager):

    def create_user(self, username, email, password=None):
        if not username:
            raise ValueError('Username cannot be null')
        if not email:
            raise ValueError('email cannot be null')
        user = self.model(
            username=username,
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password):
        user = self.create_user(
            username=username,
            email=self.normalize_email(email),
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class UserAccount(AbstractBaseUser):
    Oauth_Choices = [
        (None, 'None'),
        ('42api', '42api'),
    ]
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=60, verbose_name='email', unique=True)
    first_name = models.CharField(max_length=30, verbose_name='first name')
    last_name = models.CharField(max_length=30, verbose_name='last name')
    avatar = models.ImageField(max_length=255, upload_to=get_avatar_path, null=True, blank=True, default=set_default_avatar)
    status = models.CharField(max_length=10, default='offline')
    is_2fa = models.BooleanField(default=False)
    oauth = models.CharField(max_length=10, choices=Oauth_Choices, null=True, default=None)
    full_profile = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)

    objects = UserAccountManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def get_avatar_filename(self):
        return str(self.avatar)[str(self.avatar).index(f'avatars/{self.pk}/'):]
    
    def has_perm(self, perm, object=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True
    


class Player(models.Model):
    user = models.OneToOneField(UserAccount, related_name='player', on_delete=models.CASCADE)
    alias = models.CharField(max_length=30, unique=True)
    games_played = models.PositiveIntegerField(default=0)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    win_loss_margin = models.JSONField(default=list)
    xp = models.PositiveIntegerField(default=10)


    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if not self.alias:
            self.alias = self.user.username
        super().save(*args, **kwargs)


@receiver(post_save, sender=UserAccount)
def post_user_account_creation(sender, instance, **kwargs):
    from friends.models import FriendList, BlockList
    FriendList.objects.get_or_create(user=instance)
    Player.objects.get_or_create(user=instance)
    BlockList.objects.get_or_create(user=instance)



