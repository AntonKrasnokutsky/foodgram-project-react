from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'username',)
    list_filter = ('email', 'username',)
    fieldsets = (
        (None, {'fields': (
            'email',
            'username',
            'password',
            'first_name',
            'last_name',
        )}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'username',
                'first_name',
                'last_name',
                'password1',
                'password2',
                'is_staff',
                'is_active'
            )}
         ),
    )
    search_fields = ('email', 'username', )
    ordering = ('email',)


admin.site.register(User, CustomUserAdmin)
