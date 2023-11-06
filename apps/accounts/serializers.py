from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from .models import CustomUser, EspecialistaProfile, Especialista


User = get_user_model()


class EspecialistaCreateSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = Especialista
        fields = ('username', 'password', 'password2', 'first_name', 'last_name', 'email',
                  'telefono', 'direccion', 'nacionalidad', 'rut', 'fecha_nacimiento', 'sexo')
        # extra_kwargs = {
        #     'email': {'required': True},
        # }
        extra_kwargs = {i: {'required': True} for i in fields}
        
    def validate_email(self, value):
        if User.objects.filter(email=value).exclude(pk=self.instance.pk if self.instance else None).exists():
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
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        especialista_profile = EspecialistaProfile.objects.get(user=instance.id)
        data['id'] = instance.id
        data['especialista_profile'] = EspecialistaProfileSerializer(especialista_profile).data
        # Elimina las claves que deseas excluir
        keys_to_exclude = ['password']  # Reemplaza con los nombres de tus campos
        for key in keys_to_exclude:
            data.pop(key, None)  # Utilizamos pop para eliminar la clave si existe
        return data


class EspecialistaUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Especialista
        fields = ('username', 'first_name', 'last_name', 'email',
                  'telefono', 'direccion', 'nacionalidad', 'rut', 'fecha_nacimiento', 'sexo')
        # extra_kwargs = {
        #     'email': {'required': True},
        # }
        extra_kwargs = {i: {'required': True} for i in fields}
        
    def validate_email(self, value):
        if User.objects.filter(email=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            msg = "Email ya existe"
            raise serializers.ValidationError(msg)
        return value

    def validate_rut(self, value):
        rut = value.lower()
        if User.objects.filter(rut=rut).exclude(pk=self.instance.pk if self.instance else None).exists():
            msg = 'El rut ya se encuentra en uso'
            raise serializers.ValidationError(msg)
        return rut
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        especialista_profile = EspecialistaProfile.objects.get(user=instance.id)
        data['id'] = instance.id
        data['especialista_profile'] = EspecialistaProfileSerializer(especialista_profile).data
        # Elimina las claves que deseas excluir
        keys_to_exclude = ['password']  # Reemplaza con los nombres de tus campos
        for key in keys_to_exclude:
            data.pop(key, None)  # Utilizamos pop para eliminar la clave si existe
        return data


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
                raise serializers.ValidationError({'inicio contrato': msg})

            if inicio_contrato == termino_contrato:
                msg = 'La fecha  de inicio de contrato no puede ser igual a la fecha de termino de contrato'
                raise serializers.ValidationError({'inicio contrato': msg})
        return attrs
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id'] = instance.id
        data['nombre_completo'] = f'{instance.user.first_name} {instance.user.last_name}'
        return data

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


# Auth API django road
class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def check_user(self, validated_data):
        user = authenticate(
            username=validated_data['username'],
            password=validated_data['password']
        )
        if not user:
            raise serializers.ValidationError('Usuario no encontrado')
        return user


class User2Serializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('username', 'email')


# DJANGO WORLD
class UserRegisterSerializer2(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email')

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

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    

class UserProfileSerializer(serializers.ModelSerializer):
 
    class Meta:
        model = User
        fields = ('id', 'username', 'email')