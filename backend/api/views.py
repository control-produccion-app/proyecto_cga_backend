from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Coalesce
from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from .permissions import (
    IsAdministrador, IsJefeProduccion, IsVendedor, IsBodeguero,
    IsCatalogoOnly, IsProduccionModule, IsBodegaModule, IsVentasModule, IsReportesModule,
    WriteWithRolePermission
)
from .models import (
    Turno, Distribucion, Insumo, TipoProduccion, JornadaDiaria, Produccion,
    MovimientoBodega, ConteoBodega, Cliente, Producto, Pedido, DetallePedido,
    DetalleMovimiento, ResumenClienteDia, SaldoAcumuladoCliente
)
from .serializers import (
    TurnoSerializer, DistribucionSerializer, InsumoSerializer, TipoProduccionSerializer,
    JornadaDiariaSerializer, ProduccionSerializer, MovimientoBodegaSerializer,
    ConteoBodegaSerializer, ClienteSerializer, ProductoSerializer, PedidoSerializer,
    DetallePedidoSerializer, DetalleMovimientoSerializer
)


class TurnoViewSet(viewsets.ModelViewSet):
    queryset = Turno.objects.all()
    serializer_class = TurnoSerializer
    permission_classes = [IsAuthenticated, WriteWithRolePermission(['Administrador'])]


class DistribucionViewSet(viewsets.ModelViewSet):
    queryset = Distribucion.objects.all()
    serializer_class = DistribucionSerializer
    permission_classes = [IsAuthenticated, WriteWithRolePermission(['Administrador'])]


class InsumoViewSet(viewsets.ModelViewSet):
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer
    permission_classes = [IsAuthenticated, WriteWithRolePermission(['Administrador', 'Bodeguero'])]


class TipoProduccionViewSet(viewsets.ModelViewSet):
    queryset = TipoProduccion.objects.all()
    serializer_class = TipoProduccionSerializer
    permission_classes = [IsAuthenticated, WriteWithRolePermission(['Administrador', 'JefeProduccion'])]


class JornadaDiariaViewSet(viewsets.ModelViewSet):
    queryset = JornadaDiaria.objects.all()
    serializer_class = JornadaDiariaSerializer
    permission_classes = [IsAuthenticated, WriteWithRolePermission(['Administrador', 'JefeProduccion'])]


class ProduccionViewSet(viewsets.ModelViewSet):
    queryset = Produccion.objects.all()
    serializer_class = ProduccionSerializer
    permission_classes = [IsAuthenticated, WriteWithRolePermission(['Administrador', 'JefeProduccion'])]


class MovimientoBodegaViewSet(viewsets.ModelViewSet):
    queryset = MovimientoBodega.objects.all()
    serializer_class = MovimientoBodegaSerializer
    permission_classes = [IsAuthenticated, WriteWithRolePermission(['Administrador', 'Bodeguero'])]


class ConteoBodegaViewSet(viewsets.ModelViewSet):
    queryset = ConteoBodega.objects.all()
    serializer_class = ConteoBodegaSerializer
    permission_classes = [IsAuthenticated, WriteWithRolePermission(['Administrador', 'Bodeguero'])]


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated, WriteWithRolePermission(['Administrador', 'Vendedor'])]
    
    @action(detail=True, methods=['get'], permission_classes=[WriteWithRolePermission(['Administrador', 'Vendedor'])])
    def saldo(self, request, pk=None):
        cliente = self.get_object()
        
        saldo_acumulado_obj = SaldoAcumuladoCliente.objects.filter(id_cliente=cliente.id_cliente).first()
        resumen_aggregates = ResumenClienteDia.objects.filter(id_cliente=cliente.id_cliente).aggregate(
            total_venta=Coalesce(Sum('venta_dia'), 0),
            total_pago=Coalesce(Sum('pago_dia'), 0)
        )
        
        saldo = saldo_acumulado_obj.saldo_acumulado if saldo_acumulado_obj else 0
        
        return Response({
            'cliente_id': cliente.id_cliente,
            'cliente_nombre': cliente.nombre_cliente,
            'total_venta': resumen_aggregates['total_venta'],
            'total_pago': resumen_aggregates['total_pago'],
            'saldo_acumulado': saldo
        })


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated, WriteWithRolePermission(['Administrador', 'Vendedor'])]


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated, WriteWithRolePermission(['Administrador', 'Vendedor'])]


class DetallePedidoViewSet(viewsets.ModelViewSet):
    queryset = DetallePedido.objects.all()
    serializer_class = DetallePedidoSerializer
    permission_classes = [IsAuthenticated, WriteWithRolePermission(['Administrador', 'Vendedor'])]


class DetalleMovimientoViewSet(viewsets.ModelViewSet):
    queryset = DetalleMovimiento.objects.all()
    serializer_class = DetalleMovimientoSerializer
    permission_classes = [IsAuthenticated, WriteWithRolePermission(['Administrador', 'Vendedor'])]
    
    @action(detail=False, methods=['get'], permission_classes=[WriteWithRolePermission(['Administrador', 'JefeProduccion', 'Vendedor'])])
    def resumen_jornada(self, request):
        jornada_id = request.query_params.get('jornada_id')
        if not jornada_id:
            return Response({'error': 'jornada_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            jornada = JornadaDiaria.objects.get(id_jornada=jornada_id)
        except JornadaDiaria.DoesNotExist:
            return Response({'error': 'Jornada no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
        resumen = ResumenClienteDia.objects.filter(fecha=jornada.fecha).values(
            'id_cliente', 'nombre_cliente', 'venta_dia', 'pago_dia', 'saldo_dia'
        )
        
        response_data = []
        for item in resumen:
            response_data.append({
                'id_cliente': item['id_cliente'],
                'id_cliente__nombre_cliente': item['nombre_cliente'],
                'total_venta': item['venta_dia'],
                'total_pago': item['pago_dia'],
                'saldo_dia': item['saldo_dia']
            })
        
        return Response(response_data)


class ReportesViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, WriteWithRolePermission(['Administrador', 'JefeProduccion', 'Vendedor', 'Bodeguero'])]
    
    @action(detail=False, methods=['get'], permission_classes=[WriteWithRolePermission(['Administrador', 'JefeProduccion', 'Vendedor', 'Bodeguero'])])
    def stock_insumo(self, request):
        insumo_id = request.query_params.get('insumo_id')
        if not insumo_id:
            return Response({'error': 'insumo_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        movimientos = MovimientoBodega.objects.filter(id_insumo_id=insumo_id)
        
        entradas = movimientos.filter(tipo_movimiento='ENTRADA').aggregate(total=Coalesce(Sum('cantidad'), 0))
        salidas = movimientos.filter(tipo_movimiento='SALIDA').aggregate(total=Coalesce(Sum('cantidad'), 0))
        ajustes = movimientos.filter(tipo_movimiento='AJUSTE').aggregate(total=Coalesce(Sum('cantidad'), 0))
        
        stock_teorico = entradas['total'] - salidas['total'] + ajustes['total']
        
        ultimo_conteo = ConteoBodega.objects.filter(id_insumo_id=insumo_id).order_by('-fecha_conteo').first()
        
        return Response({
            'insumo_id': insumo_id,
            'stock_teorico': stock_teorico,
            'ultimo_conteo': ultimo_conteo.cantidad_fisica if ultimo_conteo else None,
            'fecha_ultimo_conteo': ultimo_conteo.fecha_conteo if ultimo_conteo else None,
            'diferencia': stock_teorico - (ultimo_conteo.cantidad_fisica if ultimo_conteo else 0)
        })


# Health check endpoint
from rest_framework.decorators import api_view

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({'status': 'healthy'})