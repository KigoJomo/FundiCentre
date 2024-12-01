# /fundicentre/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    model = CustomUser

    # Fields to display in the admin panel's user list
    list_display = ('email', 'first_name', 'last_name', 'user_role', 'is_active', 'is_staff')
    list_filter = ('is_staff', 'is_active', 'user_role')

    # Fields to display and allow editing in the user detail page
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'user_role')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'user_role', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

# Register the CustomUser with the CustomUserAdmin
admin.site.register(CustomUser, CustomUserAdmin)