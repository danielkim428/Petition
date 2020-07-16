from pet.models import *
from django.contrib.auth.models import User

user = User.objects.create_user('danyl', password='Sun042800*')
user.is_superuser = True
user.is_staff = True
user.save()


