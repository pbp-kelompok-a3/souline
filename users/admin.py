from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from users.models import UserProfile

from studio.models import Studio # punya faza
admin.site.register(Studio)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    
    def save_model(self, request, obj, form, change):
        # Save the user first
        super().save_model(request, obj, form, change)
        # Create or update UserProfile
        UserProfile.objects.get_or_create(
            user=obj,
            defaults={'kota': 'Jakarta'}  # SUPERUSER BARU otomatis Jakarta
        )
# KALAU DIHAPUS SUPERUSER GA ADA KOTA
# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
