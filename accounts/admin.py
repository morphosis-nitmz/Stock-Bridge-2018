from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserAdminCreationForm, UserAdminChangeForm
from .models import EmailActivation


User = get_user_model()


class UserAdmin(BaseUserAdmin):
    # The forms to change and add user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('username', 'email', 'admin')
    list_filter = ('admin', 'staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        # would have data we had fields like 'full_name'
        ('Personal info', {'fields': ('full_name', 'net_worth')}),
        ('Permissions', {'fields': ('admin', 'staff', 'is_active')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'full_name', 'net_worth', 'password1', 'password2')}
         ),
    )
    search_fields = ('username', 'email', 'full_name')
    ordering = ('username', 'email')
    filter_horizontal = ()


admin.site.register(User, UserAdmin)

# Remove Group Model from admin. We're not using it.
admin.site.unregister(Group)


class EmailActivationAdmin(admin.ModelAdmin):
    search_fields = ['email']   # Search guest users by email in admin panel

    class Meta:
        model = EmailActivation


admin.site.register(EmailActivation, EmailActivationAdmin)
