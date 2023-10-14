from django import forms
from django.core.validators import RegexValidator


# Every letter to LowerCase(charfield)
class LowerCase(forms.CharField):
    def to_python(self, value):
        return value.lower()


# Every letter to UpperCase(charfield)
class UpperCase(forms.CharField):
    def to_python(self, value):
        return value.upper()


# Every letter to Capitalize(charfield)
class Capitalize(forms.CharField):
    def to_python(self, value):
        return value.capitalize()


# si al uso en meotod clean remplza la validacion por defecto del campo
EMAIL_VALIDATOR = RegexValidator(
    regex=r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$',
    message=[
        'Introduzca una dirección de correo electrónico válida.',
    ]
)
