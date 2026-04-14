import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-bodega',
  templateUrl: './bodega.component.html',
  styleUrls: ['./bodega.component.css']
})
export class BodegaComponent implements OnInit {
  movimientos: any[] = [];
  movimientoEdit: any = null;
  nuevoMovimiento: any = {
    tipo_movimiento: 'ENTRADA'
  };
  mostrarForm = false;
  mensaje = '';
  error = '';
  cargando = false;
  insumosList: any[] = [];
  jornadasList: any[] = [];
  turnosList: any[] = [];
  cargandoListas = false;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.cargarMovimientos();
    this.cargarListas();
  }

  cargarMovimientos() {
    this.cargando = true;
    this.apiService.getMovimientosBodega().subscribe({
      next: (data) => {
        this.movimientos = Array.isArray(data) ? data : data.results || data;
        this.cargando = false;
      },
      error: (err) => {
        this.error = 'Error al cargar movimientos de bodega';
        this.cargando = false;
      }
    });
  }

  cargarListas() {
    this.cargandoListas = true;
    this.apiService.getInsumos().subscribe({
      next: (data) => {
        this.insumosList = Array.isArray(data) ? data : data.results || data;
        this.apiService.getJornadas().subscribe({
          next: (jornadasData) => {
            this.jornadasList = Array.isArray(jornadasData) ? jornadasData : jornadasData.results || jornadasData;
            this.apiService.getTurnos().subscribe({
              next: (turnosData) => {
                this.turnosList = Array.isArray(turnosData) ? turnosData : turnosData.results || turnosData;
                this.cargandoListas = false;
              },
              error: (err) => {
                this.error = 'Error al cargar turnos';
                this.cargandoListas = false;
              }
            });
          },
          error: (err) => {
            this.error = 'Error al cargar jornadas';
            this.cargandoListas = false;
          }
        });
      },
      error: (err) => {
        this.error = 'Error al cargar insumos';
        this.cargandoListas = false;
      }
    });
  }

  getJornadaNombre(id: number): string {
    const jornada = this.jornadasList.find(j => j.id_jornada === id);
    return jornada ? jornada.nombre : id;
  }

  getTurnoNombre(id: number): string {
    const turno = this.turnosList.find(t => t.id_turno === id);
    return turno ? turno.nombre : id;
  }

  crearMovimiento() {
    this.mensaje = '';
    this.error = '';
    // Sanitizar: convertir cadenas vacías a null para campos opcionales
    const movimientoSanitizado = { ...this.nuevoMovimiento };
    if (movimientoSanitizado.id_insumo === '') {
      movimientoSanitizado.id_insumo = null;
    }
    if (movimientoSanitizado.id_jornada === '') {
      movimientoSanitizado.id_jornada = null;
    }
    if (movimientoSanitizado.id_turno === '') {
      movimientoSanitizado.id_turno = null;
    }
    this.apiService.createMovimientoBodega(movimientoSanitizado).subscribe({
      next: () => {
        this.cargarMovimientos();
        this.nuevoMovimiento = { tipo_movimiento: 'ENTRADA' };
        this.mostrarForm = false;
        this.mensaje = 'Movimiento de bodega registrado exitosamente';
      },
      error: (err) => {
        this.error = 'Error al registrar movimiento de bodega';
      }
    });
  }

  editarMovimiento(movimiento: any) {
    this.movimientoEdit = { ...movimiento };
  }

  actualizarMovimiento() {
    if (this.movimientoEdit && this.movimientoEdit.id_movimiento_bodega) {
      this.mensaje = '';
      this.error = '';
      // Sanitizar: convertir cadenas vacías a null para campos opcionales
      const movimientoSanitizado = { ...this.movimientoEdit };
      if (movimientoSanitizado.id_insumo === '') {
        movimientoSanitizado.id_insumo = null;
      }
      if (movimientoSanitizado.id_jornada === '') {
        movimientoSanitizado.id_jornada = null;
      }
      if (movimientoSanitizado.id_turno === '') {
        movimientoSanitizado.id_turno = null;
      }
      this.apiService.updateMovimientoBodega(movimientoSanitizado.id_movimiento_bodega, movimientoSanitizado).subscribe({
        next: () => {
          this.cargarMovimientos();
          this.movimientoEdit = null;
          this.mensaje = 'Movimiento de bodega actualizado exitosamente';
        },
        error: (err) => {
          this.error = 'Error al actualizar movimiento de bodega';
        }
      });
    }
  }

  eliminarMovimiento(id: number) {
    if (confirm('¿Está seguro de eliminar este movimiento de bodega?')) {
      this.mensaje = '';
      this.error = '';
      this.apiService.deleteMovimientoBodega(id).subscribe({
        next: () => {
          this.cargarMovimientos();
          this.mensaje = 'Movimiento de bodega eliminado exitosamente';
        },
        error: (err) => {
          this.error = 'Error al eliminar movimiento de bodega';
        }
      });
    }
  }
}