
from django.contrib import admin
from .models import Article

admin.site.register(Article)
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профили'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'get_group')
    list_select_related = ('profile', )

    def get_role(self, instance):
        return instance.profile.get_role_display()
    get_role.short_description = 'Роль'

    def get_group(self, instance):
        return instance.profile.group
    get_group.short_description = 'Группа'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile)
