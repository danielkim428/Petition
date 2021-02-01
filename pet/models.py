from django.db import models
import datetime
from django.contrib.auth.models import User
from dateutil.relativedelta import relativedelta
from django.utils import timezone

# Create your models here.
class Post(models.Model):
    date = datetime.date.today()
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=10, null=True, blank=True)
    content = models.CharField(max_length=20000)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author_of", blank=True, null=True)
    start = models.DateField(default=date)
    end = models.DateField(default=date + relativedelta(months=1))
    state = models.IntegerField(default=0)
    stuco = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stuco_of", blank=True, null=True)
    answer = models.CharField(max_length=20000, null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.category})"

class Supporter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    posts = models.ManyToManyField(Post, blank=True, related_name="supporters")

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenter_of", blank=True, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comment_of', blank=True, null=True)
    content = models.CharField(max_length=50000)
    date = models.DateField(default=timezone.now)
    parent_comment = models.ForeignKey("self", on_delete=models.CASCADE, related_name="reply_of", blank=True, null=True)

    def __str__ (self):
        return f"{self.content}"
