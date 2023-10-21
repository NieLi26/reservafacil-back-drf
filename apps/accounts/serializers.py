from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import CustomUser, EspecialistaProfile, Especialista


User = get_user_model()


class EspecialistaCreateSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = Especialista
        # solo incluye username, password 1 y password 2
        # fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'telefono', 'direccion', 'nacionalidad', 'rut', 'fecha_nacimiento', 'sexo')
        fields = ('username', 'password', 'password2', 'first_name', 'last_name', 'email',
                  'telefono', 'direccion', 'nacionalidad', 'rut', 'fecha_nacimiento', 'sexo')
        
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            msg = "Email ya existe"
            raise serializers.ValidationError(msg)
        return value

    def validate_rut(self, value):
        rut = value.lower()
        if User.objects.filter(rut=rut).exclude(pk=self.instance.pk if self.instance else None).exists():
            msg = 'El rut ya se encuentra en uso'
            raise serializers.ValidationError(msg)
        return rut
    
    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password2'):
            msg = "Las contraseñas no coinciden."
            raise serializers.ValidationError(msg)
        return attrs

    def create(self, validated_data):
        especialista = Especialista.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            telefono=validated_data['telefono'],
            direccion=validated_data['direccion'],
            nacionalidad=validated_data['nacionalidad'],
            rut=validated_data['rut'],
            fecha_nacimiento=validated_data['fecha_nacimiento'],
            sexo=validated_data['sexo']
        )
        return especialista


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
    

class EspecialistaProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = EspecialistaProfile
        fields = ('info', 'inicio_contrato', 'termino_contrato')

    def validate(self, attrs):
        inicio_contrato = attrs.get('inicio_contrato')
        termino_contrato = attrs.get('termino_contrato')
        # ==== evitar hora de inicio mayor que la de termino, o igual
        if inicio_contrato and termino_contrato:
            if inicio_contrato > termino_contrato:
                msg = 'La fecha de inicio de contrato no puede ser mayor a la fecha de termino de contrato'
                serializers.ValidationError({'inicio_contrato': msg})

            if inicio_contrato == termino_contrato:
                msg = 'La fecha  de inicio de contrato no puede ser igual a la fecha de termino de contrato'
                serializers.ValidationError({'inicio_contrato': msg})
        return attrs
    

# Auth API
class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'email']
        # extra_kwargs = {
        #     'password': {'write_only': True}
        # }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            msg = "Email ya existe"
            raise serializers.ValidationError(msg)
        return value

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password2'):
            msg = "Las contraseñas no coinciden."
            raise serializers.ValidationError(msg)
        return attrs

    # def save(self):
    #     password = self.validated_data['password']
    #     password2 = self.validated_data['password2']

    #     if password != password2

    def create(self, validated_data):
        # ## OPCION 1
        # # Crea un nuevo usuario a partir de los datos validados
        # user = User(
        #     username=validated_data['username'],
        #     email=validated_data['email']
        # )
        # # Establece la contraseña del usuario
        # user.set_password(validated_data['password'])
        # # Guarda el usuario en la base de datos
        # user.save()
        # return user
    
        # # ## OPCION 2
        # # Crea un nuevo usuario a partir de los datos validados
        # user = User(**validated_data)
        # # Establece la contraseña del usuario
        # user.set_password(validated_data['password'])
        # # Guarda el usuario en la base de datos
        # user.save()
        # return user
    
        # OPCION 3
        # Crea un nuevo usuario a partir de los datos validados
        # Establece la contraseña del usuario
        # Guarda el usuario en la base de datos
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    

    # def update(self, instance, validated_data):
    #     # Hashear la contraseña antes de actualizar el usuario
    #     if 'password' in validated_data:
    #         password = validated_data.pop('password')
    #         instance.set_password(password)
    #     # Actualizar otros campos si es necesario
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)
    #     instance.save()
    #     return instance
