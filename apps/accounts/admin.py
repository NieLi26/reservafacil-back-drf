from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, EspecialistaProfile, AdminProfile, Especialista
# Register your models here.


# @admin.register(CustomUser)
# class CustomUserAdmin(admin.ModelAdmin):
#     list_display = ['email', 'username', 'is_staff']
    # raw_id_fields = ['email', 'username']  # Crea una barra de busqueda en el campo, debe ser fk o m2m
    # add_form = CustomUserCreationForm
    # form = CustomUserChangeForm


# adherimos el formulario personalizado con los nuevos datos al admin
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # add_form = CustomUserCreationForm  # Estos son solo para crearlos por consola
    # form = CustomUserChangeForm  # Estos son solo para crearlos por consola
    # model = CustomUser
    list_display = [
        "username",
        "email",
        "is_staff",
        "tipo"
    ]
    # fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("tipo",)}),)
    # add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("tipo",)}),)


# @admin.register(Especialista)
# class EspecialistaAdmin(admin.ModelAdmin):
#     list_display = ('username',)
#     fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("tipo",)}),)
#     add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("tipo",)}),)




@admin.register(EspecialistaProfile)
class EspecialistaProfileAdmin(admin.ModelAdmin):
    list_display = ('get_user_username', 'inicio_contrato', 'termino_contrato')

    @admin.display(description='User Username', ordering='user__username')
    def get_user_username(self, obj):
        return obj.user.username


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('get_user_username',)

    @admin.display(description='User Username', ordering='user__username')
    def get_user_username(self, obj):
        return obj.user.username
