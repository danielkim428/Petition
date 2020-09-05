from django.db import models
import datetime
from dateutil.relativedelta import relativedelta

# Create your models here.
class Post(models.Model):
    date = datetime.date.today()
    title = models.CharField(max_length=100)
    CATEGORY = [
        ('Policy', 'Policy'),
        ('Academic', 'Academic'),
        ('Food', 'Food'),
        ('Event', 'Event'),
        ('Other', 'Other'),
    ]
    category = models.CharField(max_length=20, choices = CATEGORY, null=True, blank=True)
    content = models.CharField(max_length=20000)
    authorFirst = models.CharField(max_length=20, blank=True)
    authorLast = models.CharField(max_length=20, blank=True)
    start = models.DateField(default=date)
    end = models.DateField(default=date + relativedelta(months=1))
    state = models.IntegerField(default=0)
    stuco = models.CharField(max_length=50, blank=True, default="")

    def __str__(self):
        return f"{self.title} ({self.category})"

class Supporter(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    posts = models.ManyToManyField(Post, blank=True, related_name="supporters")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
