from rest_framework import serializers
from .models import Tarifa


class TarifaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tarifa
        fields = ('valor',)

    def validate_valor(self, value):
        # valor = self.context.get('valor')
        if Tarifa.objects.filter(valor__iexact=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            msg = 'Este valor ya esta en Uso'
            raise serializers.ValidationError(msg)
        if value <= 0:
            msg = 'Valor debe ser mayor a 0'
            raise serializers.ValidationError(msg)
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id'] = instance.id
        # data['fecha'] = instance.created.strftime('%d/%m/%Y')
        data['fecha'] = instance.created.strftime('%Y/%m/%d')
        return data
