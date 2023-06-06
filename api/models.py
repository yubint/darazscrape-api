from django.db import models
from django.contrib.auth.models import AbstractUser , BaseUserManager

# Create your models here.
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email must be given')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects= UserManager()

class Product(models.Model):
    title = models.CharField(max_length=100)
    url = models.URLField()
    image_url = models.URLField()
    users = models.ManyToManyField('User', related_name='products')
    inactive_days = models.IntegerField(default=0)

class Price(models.Model):
    price = models.IntegerField()
    date = models.DateField(auto_now_add=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='prices')