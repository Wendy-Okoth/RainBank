from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, AuditLog

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role']
    list_filter = ['is_staff', 'is_superuser', 'profile__role']
    
    def get_role(self, obj):
        return obj.profile.get_role_display()
    get_role.short_description = 'Role'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'can_approve_payouts', 'can_verify_farmers', 'is_active']
    list_filter = ['role', 'can_approve_payouts', 'is_active']
    search_fields = ['user__username', 'user__email', 'employee_id']

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'object_id', 'created_at']
    list_filter = ['action', 'model_name', 'created_at']
    search_fields = ['user__username', 'object_id']
    readonly_fields = ['created_at']
