from django.contrib import admin

from .models import User, Product, Price

# Register your models here.
admin.site.register([User, Product, Price])
