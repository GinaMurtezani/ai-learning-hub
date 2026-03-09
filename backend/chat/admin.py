from django.contrib import admin

from .models import ChatAgent, ChatMessage

admin.site.register(ChatAgent)
admin.site.register(ChatMessage)
