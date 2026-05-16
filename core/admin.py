from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Shop, Medicine

# Custom User Admin
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )

# Medicine Admin (Read-Only)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'shop', 'default_price', 'discount', 'price', 'quantity')
    list_filter = ('shop',)
    search_fields = ('name', 'shop__name')
    readonly_fields = ('name', 'shop', 'default_price', 'discount', 'price', 'quantity')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

# Register your models here.
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Shop)
admin.site.register(Medicine, MedicineAdmin)
