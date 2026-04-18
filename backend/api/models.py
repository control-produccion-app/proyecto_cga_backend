from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Turno(models.Model):
    id_turno = models.AutoField(primary_key=True)
    nombre_turno = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_turno

    class Meta:
        db_table = "turno"
        constraints = [
            models.UniqueConstraint(
                fields=["nombre_turno"],
                name="unique_turno_nombre",
            )
        ]


class Distribucion(models.Model):
    id_distribucion = models.AutoField(primary_key=True)
    nombre_distribucion = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre_distribucion

    class Meta:
        db_table = "distribucion"
        constraints = [
            models.UniqueConstraint(
                fields=["nombre_distribucion"],
                name="unique_distribucion_nombre",
            )
        ]


class Insumo(models.Model):
    id_insumo = models.AutoField(primary_key=True)
    nombre_insumo = models.CharField(max_length=200)
    unidad_control = models.CharField(max_length=20)
    stock_sugerido_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.CharField(max_length=1, default="S")

    def __str__(self):
        return self.nombre_insumo

    class Meta:
        db_table = "insumo"
        constraints = [
            models.CheckConstraint(
                check=models.Q(activo__in=["S", "N"]),
                name="check_insumo_activo",
            )
        ]


class TipoProduccion(models.Model):
    id_tipo_produccion = models.AutoField(primary_key=True)
    nombre_tipo_produccion = models.CharField(max_length=200)
    id_insumo_principal = models.ForeignKey(
        Insumo,
        on_delete=models.SET_NULL,
        null=True,
        db_column="id_insumo_principal",
    )

    def __str__(self):
        return self.nombre_tipo_produccion

    class Meta:
        db_table = "tipo_produccion"


class JornadaDiaria(models.Model):
    id_jornada = models.AutoField(primary_key=True)
    fecha = models.DateField(unique=True)

    def __str__(self):
        return f"Jornada {self.fecha}"

    class Meta:
        db_table = "jornada_diaria"


class Produccion(models.Model):
    id_produccion = models.AutoField(primary_key=True)
    id_jornada = models.ForeignKey(
        JornadaDiaria,
        on_delete=models.CASCADE,
        db_column="id_jornada",
    )
    id_tipo_produccion = models.ForeignKey(
        TipoProduccion,
        on_delete=models.CASCADE,
        db_column="id_tipo_produccion",
    )
    id_turno = models.ForeignKey(
        Turno,
        on_delete=models.CASCADE,
        db_column="id_turno",
    )
    quintales = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"ProducciÃ³n {self.id_tipo_produccion} - {self.id_jornada.fecha}"

    class Meta:
        db_table = "produccion"
        unique_together = ("id_jornada", "id_tipo_produccion", "id_turno")
        indexes = [
            models.Index(fields=["id_jornada"], name="idx_prod_jornada"),
        ]


class MovimientoBodega(models.Model):
    TIPO_MOVIMIENTO_CHOICES = [
        ("ENTRADA", "Entrada"),
        ("SALIDA", "Salida"),
        ("AJUSTE", "Ajuste"),
    ]

    id_movimiento_bodega = models.AutoField(primary_key=True)
    id_insumo = models.ForeignKey(
        Insumo,
        on_delete=models.CASCADE,
        db_column="id_insumo",
    )
    fecha_movimiento = models.DateField()
    tipo_movimiento = models.CharField(
        max_length=10,
        choices=TIPO_MOVIMIENTO_CHOICES,
    )
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    id_jornada = models.ForeignKey(
        JornadaDiaria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="id_jornada",
    )
    id_turno = models.ForeignKey(
        Turno,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="id_turno",
    )

    def __str__(self):
        return f"{self.tipo_movimiento} {self.id_insumo} - {self.fecha_movimiento}"

    class Meta:
        db_table = "movimiento_bodega"
        constraints = [
            models.CheckConstraint(
                check=models.Q(tipo_movimiento__in=["ENTRADA", "SALIDA", "AJUSTE"]),
                name="check_tipo_movimiento",
            )
        ]


class ConteoBodega(models.Model):
    id_conteo_bodega = models.AutoField(primary_key=True)
    id_insumo = models.ForeignKey(
        Insumo,
        on_delete=models.CASCADE,
        db_column="id_insumo",
    )
    fecha_conteo = models.DateField()
    id_turno = models.ForeignKey(
        Turno,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="id_turno",
    )
    cantidad_fisica = models.DecimalField(max_digits=10, decimal_places=2)
    observacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Conteo {self.id_insumo} - {self.fecha_conteo}"

    class Meta:
        db_table = "conteo_bodega"
        unique_together = ("id_insumo", "fecha_conteo", "id_turno")


class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    rut = models.IntegerField(validators=[MinValueValidator(0)])
    digito_verificador = models.CharField(max_length=1)
    nombre_cliente = models.CharField(max_length=200)
    ciudad = models.CharField(max_length=100)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20)
    descuento_aplicado = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.nombre_cliente

    class Meta:
        db_table = "cliente"
        constraints = [
            models.UniqueConstraint(
                fields=["rut", "digito_verificador"],
                name="unique_cliente_rut_dv",
            )
        ]


class Producto(models.Model):
    UNIDAD_VENTA_CHOICES = [
        ("KILO", "Kilo"),
        ("UNIDAD", "Unidad"),
        ("AMBOS", "Ambos"),
    ]

    id_producto = models.AutoField(primary_key=True)
    nombre_producto = models.CharField(max_length=200)
    precio_sugerido = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_venta_base = models.CharField(
        max_length=10,
        choices=UNIDAD_VENTA_CHOICES,
        default="KILO",
    )
    id_tipo_produccion = models.ForeignKey(
        TipoProduccion,
        on_delete=models.SET_NULL,
        null=True,
        db_column="id_tipo_produccion",
    )

    def __str__(self):
        return self.nombre_producto

    class Meta:
        db_table = "producto"
        constraints = [
            models.CheckConstraint(
                check=models.Q(unidad_venta_base__in=["KILO", "UNIDAD", "AMBOS"]),
                name="check_producto_unidad_venta_base",
            )
        ]


class Pedido(models.Model):
    id_pedido = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        db_column="id_cliente",
    )
    id_distribucion = models.ForeignKey(
        Distribucion,
        on_delete=models.CASCADE,
        db_column="id_distribucion",
    )
    fecha_pedido = models.DateField()
    fecha_entrega_solicitada = models.DateField()

    def __str__(self):
        return f"Pedido {self.id_pedido} - {self.id_cliente}"

    class Meta:
        db_table = "pedido"
        indexes = [
            models.Index(fields=["id_cliente"], name="idx_pedido_cliente"),
        ]


class DetallePedido(models.Model):
    UNIDAD_MEDIDA_CHOICES = [
        ("KILO", "Kilo"),
        ("UNIDAD", "Unidad"),
    ]

    id_detalle_pedido = models.AutoField(primary_key=True)
    id_pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        db_column="id_pedido",
        related_name="detalles",
    )
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        db_column="id_producto",
    )
    cantidad_solicitada = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_medida = models.CharField(
        max_length=10,
        choices=UNIDAD_MEDIDA_CHOICES,
        default="KILO",
    )
    precio_cobrado = models.DecimalField(max_digits=10, decimal_places=2)
    descuento_porcentaje_aplicado = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Detalle {self.id_producto} - Pedido {self.id_pedido}"

    class Meta:
        db_table = "detalle_pedido"
        indexes = [
            models.Index(fields=["id_pedido"], name="idx_dp_pedido"),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(descuento_porcentaje_aplicado__gte=0)
                    & models.Q(descuento_porcentaje_aplicado__lte=100)
                ),
                name="check_descuento_detalle_pedido",
            ),
            models.CheckConstraint(
                check=models.Q(unidad_medida__in=["KILO", "UNIDAD"]),
                name="check_detalle_pedido_unidad_medida",
            ),
        ]


class DetalleMovimiento(models.Model):
    UNIDAD_MEDIDA_CHOICES = [
        ("KILO", "Kilo"),
        ("UNIDAD", "Unidad"),
    ]

    id_detalle = models.AutoField(primary_key=True)
    id_jornada = models.ForeignKey(
        JornadaDiaria,
        on_delete=models.CASCADE,
        db_column="id_jornada",
    )
    id_cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        db_column="id_cliente",
    )
    id_distribucion = models.ForeignKey(
        Distribucion,
        on_delete=models.CASCADE,
        db_column="id_distribucion",
    )
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        db_column="id_producto",
    )
    id_pedido = models.ForeignKey(
        Pedido,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="id_pedido",
    )
    precio_cobrado = models.DecimalField(max_digits=10, decimal_places=2)
    descuento_porcentaje_aplicado = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        blank=True,
    )
    cantidad_entregada = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unidad_medida = models.CharField(
        max_length=10,
        choices=UNIDAD_MEDIDA_CHOICES,
        default="KILO",
    )




    cancelacion = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Movimiento {self.id_cliente} - {self.id_jornada.fecha}"



    @property
    def venta_linea(self):
        return self.precio_cobrado * self.cantidad_entregada

    class Meta:
        db_table = "detalle_movimiento"
        indexes = [
            models.Index(fields=["id_cliente"], name="idx_dm_cliente"),
            models.Index(fields=["id_jornada"], name="idx_dm_jornada"),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(descuento_porcentaje_aplicado__gte=0)
                    & models.Q(descuento_porcentaje_aplicado__lte=100)
                ),
                name="check_descuento_detalle_movimiento",
            ),
            models.CheckConstraint(
                check=models.Q(unidad_medida__in=["KILO", "UNIDAD"]),
                name="check_detalle_movimiento_unidad_medida",
            ),
        ]


class ResumenClienteDia(models.Model):
    id = models.BigIntegerField(primary_key=True)
    fecha = models.DateField()
    id_cliente = models.BigIntegerField()
    rut = models.IntegerField()
    digito_verificador = models.CharField(max_length=1)
    nombre_cliente = models.CharField(max_length=150)
    venta_dia = models.DecimalField(max_digits=20, decimal_places=2)
    pago_dia = models.DecimalField(max_digits=20, decimal_places=2)
    saldo_dia = models.DecimalField(max_digits=20, decimal_places=2)

    class Meta:
        managed = False
        db_table = "vw_resumen_cliente_dia"


class SaldoAcumuladoCliente(models.Model):
    id = models.BigIntegerField(primary_key=True)
    id_cliente = models.BigIntegerField()
    rut = models.IntegerField()
    digito_verificador = models.CharField(max_length=1)
    nombre_cliente = models.CharField(max_length=150)
    saldo_acumulado = models.DecimalField(max_digits=20, decimal_places=2)

    class Meta:
        managed = False
        db_table = "vw_saldo_acumulado_cliente"
