from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import FriendList, FriendRequest

# Register your models here.

class FriendRequestAdmin(UserAdmin):
    list_display = ('sender', 'receiver', 'is_active', 'timestamp')
    search_fields = ('sender', 'receiver')
    readonly_fields = ('is_active', 'timestamp')

    ordering = ['sender']
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(FriendRequest, FriendRequestAdmin)