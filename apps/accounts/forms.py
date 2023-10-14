
from django.contrib.auth.models import Group
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import CustomUser, EspecialistaProfile, Especialista

User = get_user_model()

# estos solo funcionaran si lo uso como forms en template
class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ("tipo",)


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ("username", "email", "tipo")


# class CustomUserLoginForm(AuthenticationForm):
#     pass


class EspecialistaCreationForm(UserCreationForm):

    class Meta:
        model = Especialista
        # solo incluye username, password 1 y password 2
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'telefono', 'direccion', 'nacionalidad', 'rut', 'fecha_nacimiento', 'sexo')

    def clean_rut(self):
        rut = self.cleaned_data['rut']
        rut = rut.lower()
        if User.objects.filter(rut=rut).exclude(pk=self.instance.pk).exists():
            msg = 'El rut ya se encuentra en uso'
            raise forms.ValidationError(msg)
        return rut

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            if user.tipo == "ESP":
                group = Group.objects.get(name='Especialista')
                user.groups.add(group)
            elif user.tipo == "ADM":
                group = Group.objects.get(name='Administrador')
                user.groups.add(group)
        return user


class EspecialistaChangeForm(UserChangeForm):

    class Meta:
        model = Especialista
        # solo incluye username, password 1 y password 2
        fields = ('username', 'first_name', 'last_name', 'email', 'telefono', 'direccion', 'nacionalidad', 'rut', 'fecha_nacimiento', 'sexo')

    def clean_rut(self):
        rut = self.cleaned_data['rut']
        rut = rut.lower()
        if User.objects.filter(rut=rut).exclude(pk=self.instance.pk).exists():
            msg = 'El rut ya se encuentra en uso'
            raise forms.ValidationError(msg)
        return rut


# class EspecialistaForm(forms.ModelForm):
#     """
#     Usamos set_password por que en este caso, los datos se validan solo con el Modelo
#     """
#     password1 = forms.CharField(widget=forms.PasswordInput)
#     password2 = forms.CharField(widget=forms.PasswordInput)

#     class Meta:
#         model = Especialista
#         fields = (
#             'username', 'first_name', 'last_name', 'email',
#             'telefono', 'direccion', 'nacionalidad',
#             'rut', 'fecha_nacimiento', 'sexo'
#         )

#     def clean(self):
#         cleaned_data = self.cleaned_data
#         password1 = cleaned_data.get('password1')
#         password2 = cleaned_data.get('password2')
#         if password1 and password2 and password1 != password2:
#             msg = "Las contrasenas no son iguales"
#             self.add_error('password2', msg)
#         return cleaned_data
    
#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data['password1'])
#         if commit:
#             user.save()
#         return user


class EspecialistaProfileForm(forms.ModelForm):

    class Meta:
        model = EspecialistaProfile
        fields = ('info', 'inicio_contrato', 'termino_contrato')

    def clean(self):
        clean_data = super().clean()
        inicio_contrato = clean_data.get('inicio_contrato')
        termino_contrato = clean_data.get('termino_contrato')
        # ==== evitar hora de inicio mayor que la de termino, o igual
        if inicio_contrato and termino_contrato:
            if inicio_contrato > termino_contrato:
                msg = 'La fecha de inicio de contrato no puede ser mayor a la fecha de termino de contrato'
                self.add_error('inicio_contrato', msg)
            if inicio_contrato == termino_contrato:
                msg = 'La fecha  de inicio de contrato no puede ser igual a la fecha de termino de contrato'
                self.add_error('inicio_contrato', msg)
        return clean_data