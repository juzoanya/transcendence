from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserAccount, Player

# Register your models here.

class AccountAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'status', 'is_active', 'is_admin', 'last_login', 'date_joined')
    search_fields = ('username', 'email')
    readonly_fields = ('id', 'date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets =()

class PlayerAdmin(UserAdmin):
    list_display = ('user', 'display_name', 'games_played', 'wins', 'losses')
    search_fields = ('user', 'display_name')
    readonly_fields = ('id', 'games_played', 'wins', 'losses')

    ordering = ['user']
    filter_horizontal = ()
    list_filter = ()
    fieldsets =()


admin.site.register(UserAccount, AccountAdmin)
admin.site.register(Player, PlayerAdmin)