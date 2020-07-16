from django.contrib import admin
from .models import *

# Register your models here.
class SupporterInline(admin.StackedInline):
    model = Supporter.posts.through
    extra = 1

class PostAdmin(admin.ModelAdmin):
    inlines = [SupporterInline]

class SupporterAdmin(admin.ModelAdmin):
    filter_horizontal = ("posts",)


admin.site.register(Post, PostAdmin)
admin.site.register(Supporter, SupporterAdmin)