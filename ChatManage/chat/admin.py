from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Register your models here.

from .models import ChatUser, ApiKey


# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class ChatUserInline(admin.StackedInline):
    model = ChatUser
    can_delete = False
    verbose_name_plural = 'ChatUser'


# Define a new User admin


class UserAdmin(BaseUserAdmin):
    inlines = (ChatUserInline,)
    list_display = ("username", "email", "is_staff")


class ChatAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_vip')
    actions = [
        'make_chat_user_can_use_api',
        'make_chat_user_not_use_api'
    ]

    @admin.action(description="允许用户使用ChatGPT接口")
    def make_chat_user_can_use_api(self, request, queryset):
        queryset.update(is_vip=True)

    @admin.action(description="禁止用户使用ChatGPT接口")
    def make_chat_user_not_use_api(self, request, queryset):
        queryset.update(is_vip=False)


class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ('value', 'call_count', 'is_valid')
    list_editable = ('is_valid',)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(ChatUser, ChatAdmin)
admin.site.register(ApiKey, ApiKeyAdmin)
admin.site.disable_action('delete_selected')
