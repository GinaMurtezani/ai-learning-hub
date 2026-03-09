from django.contrib import admin

from .models import Achievement, UserAchievement, UserProfile

admin.site.register(UserProfile)
admin.site.register(Achievement)
admin.site.register(UserAchievement)
