# main/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    Article,
    MoneyOperations,
    Groups,
    Subjects,
    Grades,
    Events,
    Achievements,
    Orders,
    Merch,
    Registrations,
    EventRoles,
    StudentGroupMembership,
    Profile,
)

# ========== Профиль пользователя ==========
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профили'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role')
    list_select_related = ('profile', )

    def get_role(self, instance):
        return instance.profile.get_role_display()
    get_role.short_description = 'Роль'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile)


# ========== Статьи ==========
admin.site.register(Article)


# ========== Группы ==========
class StudentGroupMembershipInline(admin.TabularInline):
    model = StudentGroupMembership
    extra = 1
    autocomplete_fields = ['user']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user__profile__role='ST')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(profile__role='ST').order_by('last_name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Groups)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('group_name',)
    search_fields = ('group_name',)
    inlines = [StudentGroupMembershipInline]


# ========== Предметы ==========
admin.site.register(Subjects)


# ========== Оценки ==========
@admin.register(Grades)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'subject_id', 'grade')
    list_select_related = ('student_id', 'subject_id')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "student_id":
            kwargs["queryset"] = db_field.remote_field.model.objects.filter(profile__role='ST').order_by('last_name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# ========== Мероприятия ==========
admin.site.register(Events)
admin.site.register(EventRoles)
admin.site.register(Registrations)


# ========== Достижения ==========
admin.site.register(Achievements)


# ========== Заказы ==========
admin.site.register(Orders)


# ========== Товары ==========
admin.site.register(Merch)


# ========== Финансовые операции ==========
admin.site.register(MoneyOperations)