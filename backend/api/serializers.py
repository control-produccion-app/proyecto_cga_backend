from rest_framework import serializers
from .models import (
    Turno, Distribucion, Insumo, TipoProduccion, JornadaDiaria, Produccion,
    CierreTurno, MovimientoBodega, ConteoBodega, Cliente, Producto, Pedido,
    DetallePedido, DetalleMovimiento, DetalleRepartoTurno
)


class TurnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Turno
        fields = '__all__'


class DistribucionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distribucion
        fields = '__all__'


class InsumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insumo
        fields = '__all__'


class TipoProduccionSerializer(serializers.ModelSerializer):
    insumo_principal_nombre = serializers.CharField(
        source='id_insumo_principal.nombre_insumo',
        read_only=True
    )

    class Meta:
        model = TipoProduccion
        fields = '__all__'


class JornadaDiariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = JornadaDiaria
        fields = '__all__'


class ProduccionSerializer(serializers.ModelSerializer):
    tipo_produccion_nombre = serializers.CharField(
        source='id_tipo_produccion.nombre_tipo_produccion',
        read_only=True
    )
    turno_nombre = serializers.CharField(
        source='id_turno.nombre_turno',
        read_only=True
    )
    jornada_fecha = serializers.DateField(
        source='id_jornada.fecha',
        read_only=True
    )

    class Meta:
        model = Produccion
        fields = '__all__'


class CierreTurnoSerializer(serializers.ModelSerializer):
    jornada_fecha = serializers.DateField(
        source='id_jornada.fecha',
        read_only=True
    )
    turno_nombre = serializers.CharField(
        source='id_turno.nombre_turno',
        read_only=True
    )

    class Meta:
        model = CierreTurno
        fields = '__all__'

    def validate(self, attrs):
        ajuste = attrs.get(
            'ajuste_por_error_kg',
            getattr(self.instance, 'ajuste_por_error_kg', 0) if self.instance else 0
        )
        observacion = attrs.get(
            'observacion',
            getattr(self.instance, 'observacion', None) if self.instance else None
        )

        if ajuste != 0 and not observacion:
            raise serializers.ValidationError({
                'observacion': 'La observación es obligatoria cuando existe ajuste por error.'
            })

        return attrs


class MovimientoBodegaSerializer(serializers.ModelSerializer):
    insumo_nombre = serializers.CharField(
        source='id_insumo.nombre_insumo',
        read_only=True
    )
    turno_nombre = serializers.CharField(
        source='id_turno.nombre_turno',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = MovimientoBodega
        fields = '__all__'


class ConteoBodegaSerializer(serializers.ModelSerializer):
    insumo_nombre = serializers.CharField(
        source='id_insumo.nombre_insumo',
        read_only=True
    )
    turno_nombre = serializers.CharField(
        source='id_turno.nombre_turno',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = ConteoBodega
        fields = '__all__'


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'


class ProductoSerializer(serializers.ModelSerializer):
    tipo_produccion_nombre = serializers.CharField(
        source='id_tipo_produccion.nombre_tipo_produccion',
        read_only=True
    )

    class Meta:
        model = Producto
        fields = '__all__'


class DetallePedidoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(
        source='id_producto.nombre_producto',
        read_only=True
    )

    class Meta:
        model = DetallePedido
        fields = '__all__'


class PedidoSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(
        source='id_cliente.nombre_cliente',
        read_only=True
    )
    distribucion_nombre = serializers.CharField(
        source='id_distribucion.nombre_distribucion',
        read_only=True
    )
    detalles = DetallePedidoSerializer(many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = '__all__'


class DetalleMovimientoSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(
        source='id_cliente.nombre_cliente',
        read_only=True
    )
    producto_nombre = serializers.CharField(
        source='id_producto.nombre_producto',
        read_only=True
    )
    distribucion_nombre = serializers.CharField(
        source='id_distribucion.nombre_distribucion',
        read_only=True
    )
    jornada_fecha = serializers.DateField(
        source='id_jornada.fecha',
        read_only=True
    )
    turno_nombre = serializers.CharField(
        source='id_turno.nombre_turno',
        read_only=True,
        allow_null=True
    )
    id_turno = serializers.PrimaryKeyRelatedField(
        queryset=Turno.objects.all(),
        required=False,
        allow_null=True
    )
    venta_linea = serializers.DecimalField(
        max_digits=20,
        decimal_places=2,
        read_only=True
    )
    kilos = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        write_only=True,
        required=False,
        help_text="Compatibilidad frontend"
    )

    class Meta:
        model = DetalleMovimiento
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['venta_linea'] = instance.venta_linea

        if instance.unidad_medida == 'KILO':
            representation['kilos'] = instance.cantidad_entregada
        else:
            representation['kilos'] = 0

        return representation

    def create(self, validated_data):
        kilos = validated_data.pop('kilos', None)

        if kilos is not None:
            validated_data['cantidad_entregada'] = kilos
            if 'unidad_medida' not in validated_data:
                validated_data['unidad_medida'] = 'KILO'

        return super().create(validated_data)

    def update(self, instance, validated_data):
        kilos = validated_data.pop('kilos', None)

        if kilos is not None:
            validated_data['cantidad_entregada'] = kilos
            if 'unidad_medida' not in validated_data:
                validated_data['unidad_medida'] = 'KILO'

        return super().update(instance, validated_data)


class DetalleRepartoTurnoSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(
        source='id_cliente.nombre_cliente',
        read_only=True
    )
    distribucion_nombre = serializers.CharField(
        source='id_distribucion.nombre_distribucion',
        read_only=True
    )
    jornada_fecha = serializers.DateField(
        source='id_jornada.fecha',
        read_only=True
    )
    turno_nombre = serializers.CharField(
        source='id_turno.nombre_turno',
        read_only=True
    )

    class Meta:
        model = DetalleRepartoTurno
        fields = '__all__'