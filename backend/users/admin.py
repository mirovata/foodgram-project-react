from django.contrib import admin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy

from users.models import User, UserSubscribe


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = (
        'email',
        'first_name',
        'last_name'
    )
    list_filter = ('email', 'first_name')


@admin.register(UserSubscribe)
class UserSubscribe(admin.ModelAdmin):

    list_display = (
        'author',
        'follower'
    )


admin.site.empty_value_display = 'Не задано'
admin.site.unregister(TokenProxy)
admin.site.unregister(Group)
