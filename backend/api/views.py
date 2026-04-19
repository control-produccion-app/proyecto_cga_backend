from datetime import date
from decimal import Decimal

from django.db import connection
from django.db.models import Sum
from django.utils.dateparse import parse_date

from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import (
    Turno,
    Distribucion,
    Insumo,
    TipoProduccion,
    JornadaDiaria,
    Produccion,
    MovimientoBodega,
    ConteoBodega,
    Cliente,
    Producto,
    Pedido,
    DetallePedido,
    DetalleMovimiento,
    ResumenClienteDia,
    SaldoAcumuladoCliente,
)

from .serializers import (
    TurnoSerializer,
    DistribucionSerializer,
    InsumoSerializer,
    TipoProduccionSerializer,
    JornadaDiariaSerializer,
    ProduccionSerializer,
    MovimientoBodegaSerializer,
    ConteoBodegaSerializer,
    ClienteSerializer,
    ProductoSerializer,
    PedidoSerializer,
    DetallePedidoSerializer,
    DetalleMovimientoSerializer,
)

from .permissions import (
    EstaAutenticadoLecturaORolEscritura,
    EstaAutenticadoYConRol,
)

# =========================================================
# ROLES OFICIALES DEL SISTEMA
# =========================================================

ROL_ADMINISTRADOR = "Administrador"
ROL_ENCARGADO_TURNO = "Encargado de turno"

ROLES_ADMIN = [ROL_ADMINISTRADOR]
ROLES_OPERACION = [ROL_ADMINISTRADOR, ROL_ENCARGADO_TURNO]

# =========================================================
# CATÃLOGOS BASE
# =========================================================

class TurnoViewSet(viewsets.ModelViewSet):
    queryset = Turno.objects.all()
    serializer_class = TurnoSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_ADMIN


class DistribucionViewSet(viewsets.ModelViewSet):
    queryset = Distribucion.objects.all()
    serializer_class = DistribucionSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_ADMIN


class InsumoViewSet(viewsets.ModelViewSet):
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_ADMIN


class TipoProduccionViewSet(viewsets.ModelViewSet):
    queryset = TipoProduccion.objects.all()
    serializer_class = TipoProduccionSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_ADMIN


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_ADMIN


# =========================================================
# PRODUCCIÃ“N
# =========================================================

class JornadaDiariaViewSet(viewsets.ModelViewSet):
    queryset = JornadaDiaria.objects.all()
    serializer_class = JornadaDiariaSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_OPERACION


class ProduccionViewSet(viewsets.ModelViewSet):
    queryset = Produccion.objects.all()
    serializer_class = ProduccionSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_OPERACION

# =========================================================
# BODEGA
# =========================================================

class MovimientoBodegaViewSet(viewsets.ModelViewSet):
    queryset = MovimientoBodega.objects.all()
    serializer_class = MovimientoBodegaSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_OPERACION


class ConteoBodegaViewSet(viewsets.ModelViewSet):
    queryset = ConteoBodega.objects.all()
    serializer_class = ConteoBodegaSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_OPERACION


# =========================================================
# CLIENTES / PEDIDOS / MOVIMIENTOS COMERCIALES
# =========================================================

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_ADMIN

    @action(detail=True, methods=["get"])
    def saldo(self, request, pk=None):
        self.roles_permitidos = ROLES_ADMIN
        if not EstaAutenticadoYConRol().has_permission(request, self):
            return Response(
                {"detail": "No tiene permisos para acceder a este mÃ³dulo."},
                status=status.HTTP_403_FORBIDDEN,
            )

        cliente = self.get_object()

        saldo_acumulado_obj = (
            SaldoAcumuladoCliente.objects
            .filter(id_cliente=cliente.id_cliente)
            .first()
        )

        resumen = (
            ResumenClienteDia.objects
            .filter(id_cliente=cliente.id_cliente)
            .aggregate(
                total_venta=Sum("venta_dia"),
                total_pago=Sum("pago_dia"),
            )
        )

        total_venta = resumen["total_venta"] or Decimal("0.00")
        total_pago = resumen["total_pago"] or Decimal("0.00")
        saldo_acumulado = (
            saldo_acumulado_obj.saldo_acumulado
            if saldo_acumulado_obj
            else Decimal("0.00")
        )

        return Response({
            "cliente_id": cliente.id_cliente,
            "cliente_nombre": cliente.nombre_cliente,
            "total_venta": total_venta,
            "total_pago": total_pago,
            "saldo_acumulado": saldo_acumulado,
        })




class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_OPERACION


class DetallePedidoViewSet(viewsets.ModelViewSet):
    queryset = DetallePedido.objects.all()
    serializer_class = DetallePedidoSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_OPERACION


class DetalleMovimientoViewSet(viewsets.ModelViewSet):
    queryset = DetalleMovimiento.objects.all()
    serializer_class = DetalleMovimientoSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_OPERACION

    @action(detail=False, methods=["get"])
    def resumen_jornada(self, request):
        self.roles_permitidos = ROLES_ADMIN

        if not EstaAutenticadoYConRol().has_permission(request, self):
            return Response(
                {"detail": "No tiene permisos para acceder a este mÃ³dulo."},
                status=status.HTTP_403_FORBIDDEN,
            )

        jornada_id = request.query_params.get("jornada_id")

        if not jornada_id:
            return Response(
                {"error": "jornada_id es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            jornada = JornadaDiaria.objects.get(id_jornada=jornada_id)
        except JornadaDiaria.DoesNotExist:
            return Response(
                {"error": "Jornada no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )

        resumen = (
            ResumenClienteDia.objects
            .filter(fecha=jornada.fecha)
            .values(
                "id_cliente",
                "nombre_cliente",
                "venta_dia",
                "pago_dia",
                "saldo_dia",
            )
        )

        respuesta = []

        for item in resumen:
            respuesta.append({
                "id_cliente": item["id_cliente"],
                "cliente_nombre": item["nombre_cliente"],
                "total_venta": item["venta_dia"],
                "total_pago": item["pago_dia"],
                "saldo_dia": item["saldo_dia"],
            })

        return Response(respuesta)


# =========================================================
# REPORTES
# =========================================================

class ReportesViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, EstaAutenticadoYConRol]
    roles_permitidos = ROLES_ADMIN

    @action(detail=False, methods=["get"])
    def stock_insumo(self, request):
        insumo_id = request.query_params.get("insumo_id")
        fecha_param = request.query_params.get("fecha")

        if not insumo_id:
            return Response(
                {"error": "insumo_id es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        fecha_consulta = date.today()

        if fecha_param:
            fecha_parseada = parse_date(fecha_param)

            if not fecha_parseada:
                return Response(
                    {"error": "fecha debe tener formato YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            fecha_consulta = fecha_parseada

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT fn_stock_insumo_fecha(%s, %s)",
                [insumo_id, fecha_consulta],
            )
            stock_teorico = cursor.fetchone()[0]

        ultimo_conteo = (
            ConteoBodega.objects
            .filter(id_insumo_id=insumo_id)
            .order_by("-fecha_conteo")
            .first()
        )

        cantidad_fisica = ultimo_conteo.cantidad_fisica if ultimo_conteo else None

        diferencia = None
        if cantidad_fisica is not None:
            diferencia = stock_teorico - cantidad_fisica

        return Response({
            "insumo_id": insumo_id,
            "fecha_consulta": fecha_consulta,
            "stock_teorico": stock_teorico,
            "ultimo_conteo": cantidad_fisica,
            "fecha_ultimo_conteo": ultimo_conteo.fecha_conteo if ultimo_conteo else None,
            "diferencia": diferencia,
        })

# =========================================================
# USUARIO AUTENTICADO
# =========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def usuario_actual(request):
    usuario = request.user

    roles = list(
        usuario.groups.values_list("name", flat=True)
    )

    return Response({
        "id": usuario.id,
        "username": usuario.username,
        "is_superuser": usuario.is_superuser,
        "roles": roles,
    })

# =========================================================
# HEALTH CHECK
# =========================================================

@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return Response({"status": "healthy"})
