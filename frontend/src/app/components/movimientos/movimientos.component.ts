import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-movimientos',
  templateUrl: './movimientos.component.html',
  styleUrls: ['./movimientos.component.css']
})
export class MovimientosComponent implements OnInit {
  movimientos: any[] = [];
  movimientoEdit: any = null;
  nuevoMovimiento: any = {
    precio_cobrado: 0,
    descuento_porcentaje_aplicado: 0,
    kilos: 0,
    cancelacion: 0,
    unidad_medida: 'KILO'
  };
  mostrarForm = false;
  mensaje = '';
  error = '';
  cargando = false;
  cargandoListas = false;

  // Listas para dropdowns
  jornadasList: any[] = [];
  clientesList: any[] = [];
  distribucionesList: any[] = [];
  productosList: any[] = [];
  pedidosList: any[] = [];

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.cargarMovimientos();
    this.cargarListas();
  }

  cargarMovimientos() {
    this.cargando = true;
    this.apiService.getMovimientos().subscribe({
      next: (data) => {
        this.movimientos = Array.isArray(data) ? data : data.results || data;
        this.cargando = false;
      },
      error: (err) => {
        if (err.status !== 401) {
          this.error = 'Error al cargar movimientos';
        }
        this.cargando = false;
      }
    });
  }

  cargarListas() {
    this.cargandoListas = true;
    
    // Cargar todas las listas en paralelo
    this.apiService.getJornadas().subscribe({
      next: (data) => {
        this.jornadasList = Array.isArray(data) ? data : data.results || data;
        this.verificarCargaCompleta();
      },
      error: (err) => {
        this.error = 'Error al cargar jornadas';
        this.cargandoListas = false;
      }
    });

    this.apiService.getClientes().subscribe({
      next: (data) => {
        this.clientesList = Array.isArray(data) ? data : data.results || data;
        this.verificarCargaCompleta();
      },
      error: (err) => {
        this.error = 'Error al cargar clientes';
        this.cargandoListas = false;
      }
    });

    this.apiService.getDistribuciones().subscribe({
      next: (data) => {
        this.distribucionesList = Array.isArray(data) ? data : data.results || data;
        this.verificarCargaCompleta();
      },
      error: (err) => {
        this.error = 'Error al cargar distribuciones';
        this.cargandoListas = false;
      }
    });

    this.apiService.getProductos().subscribe({
      next: (data) => {
        this.productosList = Array.isArray(data) ? data : data.results || data;
        this.verificarCargaCompleta();
      },
      error: (err) => {
        this.error = 'Error al cargar productos';
        this.cargandoListas = false;
      }
    });

    this.apiService.getPedidos().subscribe({
      next: (data) => {
        this.pedidosList = Array.isArray(data) ? data : data.results || data;
        this.verificarCargaCompleta();
      },
      error: (err) => {
        this.error = 'Error al cargar pedidos';
        this.cargandoListas = false;
      }
    });
  }

  verificarCargaCompleta() {
    if (this.jornadasList.length > 0 && this.clientesList.length > 0 && 
        this.distribucionesList.length > 0 && this.productosList.length > 0 && 
        this.pedidosList.length > 0) {
      this.cargandoListas = false;
    }
  }

  crearMovimiento() {
    this.mensaje = '';
    this.error = '';
    
    // Ensure numeric values
    const datos = {
      id_jornada: parseInt(this.nuevoMovimiento.id_jornada),
      id_cliente: parseInt(this.nuevoMovimiento.id_cliente),
      id_distribucion: parseInt(this.nuevoMovimiento.id_distribucion),
      id_producto: parseInt(this.nuevoMovimiento.id_producto),
      id_pedido: this.nuevoMovimiento.id_pedido ? parseInt(this.nuevoMovimiento.id_pedido) : null,
      precio_cobrado: parseFloat(this.nuevoMovimiento.precio_cobrado),
      descuento_porcentaje_aplicado: this.nuevoMovimiento.descuento_porcentaje_aplicado ? 
        parseFloat(this.nuevoMovimiento.descuento_porcentaje_aplicado) : 0,
      kilos: parseFloat(this.nuevoMovimiento.kilos),
      cancelacion: parseFloat(this.nuevoMovimiento.cancelacion),
      unidad_medida: this.nuevoMovimiento.unidad_medida || 'KILO'
    };
    
    console.log('Enviando movimiento:', datos);
    this.apiService.createMovimiento(datos).subscribe({
      next: () => {
        this.cargarMovimientos();
        this.nuevoMovimiento = {
          precio_cobrado: 0,
          descuento_porcentaje_aplicado: 0,
          kilos: 0,
          cancelacion: 0
        };
        this.mostrarForm = false;
        this.mensaje = 'Movimiento registrado exitosamente';
      },
      error: (err) => {
        console.error('Error detallado:', err);
        this.error = 'Error al registrar movimiento: ' + (err.error?.detail || err.message || JSON.stringify(err.error) || 'Verifique los datos');
      }
    });
  }

  editarMovimiento(movimiento: any) {
    this.movimientoEdit = { ...movimiento };
  }

  actualizarMovimiento() {
    if (this.movimientoEdit && this.movimientoEdit.id_detalle) {
      this.mensaje = '';
      this.error = '';
      
      // Ensure numeric values
      const datos = {
        id_jornada: parseInt(this.movimientoEdit.id_jornada),
        id_cliente: parseInt(this.movimientoEdit.id_cliente),
        id_distribucion: parseInt(this.movimientoEdit.id_distribucion),
        id_producto: parseInt(this.movimientoEdit.id_producto),
        id_pedido: this.movimientoEdit.id_pedido ? parseInt(this.movimientoEdit.id_pedido) : null,
        precio_cobrado: parseFloat(this.movimientoEdit.precio_cobrado),
        descuento_porcentaje_aplicado: this.movimientoEdit.descuento_porcentaje_aplicado ? 
          parseFloat(this.movimientoEdit.descuento_porcentaje_aplicado) : 0,
        kilos: parseFloat(this.movimientoEdit.kilos),
        cancelacion: parseFloat(this.movimientoEdit.cancelacion),
        unidad_medida: this.movimientoEdit.unidad_medida || 'KILO'
      };
      
      console.log('Actualizando movimiento:', datos);
      this.apiService.updateMovimiento(this.movimientoEdit.id_detalle, datos).subscribe({
        next: () => {
          this.cargarMovimientos();
          this.movimientoEdit = null;
          this.mensaje = 'Movimiento actualizado exitosamente';
        },
        error: (err) => {
          console.error('Error detallado:', err);
          this.error = 'Error al actualizar movimiento: ' + (err.error?.detail || err.message || JSON.stringify(err.error) || 'Verifique los datos');
        }
      });
    }
  }

  eliminarMovimiento(id: number) {
    if (confirm('¿Está seguro de eliminar este movimiento?')) {
      this.mensaje = '';
      this.error = '';
      this.apiService.deleteMovimiento(id).subscribe({
        next: () => {
          this.cargarMovimientos();
          this.mensaje = 'Movimiento eliminado exitosamente';
        },
        error: (err) => {
          this.error = 'Error al eliminar movimiento';
        }
      });
    }
  }
}