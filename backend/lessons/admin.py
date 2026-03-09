from django.contrib import admin

from .models import Lesson, LearningPath, LessonProgress

admin.site.register(LearningPath)
admin.site.register(Lesson)
admin.site.register(LessonProgress)
