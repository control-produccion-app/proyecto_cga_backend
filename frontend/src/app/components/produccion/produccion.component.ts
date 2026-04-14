import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-produccion',
  templateUrl: './produccion.component.html',
  styleUrls: ['./produccion.component.css']
})
export class ProduccionComponent implements OnInit {
  producciones: any[] = [];
  produccionEdit: any = null;
  nuevaProduccion: any = {
    quintales: 0
  };
  mostrarForm = false;
  mensaje = '';
  error = '';
  cargando = false;
  jornadasList: any[] = [];
  tiposProduccionList: any[] = [];
  turnosList: any[] = [];
  cargandoListas = false;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.cargarProducciones();
    this.cargarListas();
  }

  cargarProducciones() {
    this.cargando = true;
    this.apiService.getProducciones().subscribe({
      next: (data) => {
        this.producciones = Array.isArray(data) ? data : data.results || data;
        this.cargando = false;
      },
      error: (err) => {
        this.error = 'Error al cargar producción';
        this.cargando = false;
      }
    });
  }

  cargarListas() {
    this.cargandoListas = true;
    this.apiService.getJornadas().subscribe({
      next: (data) => {
        this.jornadasList = Array.isArray(data) ? data : data.results || data;
        this.apiService.getTiposProduccion().subscribe({
          next: (tiposData) => {
            this.tiposProduccionList = Array.isArray(tiposData) ? tiposData : tiposData.results || tiposData;
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
            this.error = 'Error al cargar tipos de producción';
            this.cargandoListas = false;
          }
        });
      },
      error: (err) => {
        this.error = 'Error al cargar jornadas';
        this.cargandoListas = false;
      }
    });
  }

  crearProduccion() {
    this.mensaje = '';
    this.error = '';
    
    // Ensure numeric values for foreign keys
    const datos = {
      id_jornada: parseInt(this.nuevaProduccion.id_jornada),
      id_tipo_produccion: parseInt(this.nuevaProduccion.id_tipo_produccion),
      id_turno: parseInt(this.nuevaProduccion.id_turno),
      quintales: parseFloat(this.nuevaProduccion.quintales)
    };
    
    console.log('Enviando datos procesados:', datos);
    this.apiService.createProduccion(datos).subscribe({
      next: () => {
        this.cargarProducciones();
        this.nuevaProduccion = { quintales: 0 };
        this.mostrarForm = false;
        this.mensaje = 'Producción registrada exitosamente';
      },
      error: (err) => {
        console.error('Error detallado:', err);
        this.error = 'Error al registrar producción: ' + (err.error?.detail || err.message || JSON.stringify(err.error) || 'Verifique los datos');
      }
    });
  }

  editarProduccion(produccion: any) {
    this.produccionEdit = { ...produccion };
  }

  actualizarProduccion() {
    if (this.produccionEdit && this.produccionEdit.id_produccion) {
      this.mensaje = '';
      this.error = '';
      
      // Ensure numeric values for foreign keys
      const datos = {
        id_jornada: parseInt(this.produccionEdit.id_jornada),
        id_tipo_produccion: parseInt(this.produccionEdit.id_tipo_produccion),
        id_turno: parseInt(this.produccionEdit.id_turno),
        quintales: parseFloat(this.produccionEdit.quintales)
      };
      
      console.log('Actualizando producción con datos procesados:', datos);
      this.apiService.updateProduccion(this.produccionEdit.id_produccion, datos).subscribe({
        next: () => {
          this.cargarProducciones();
          this.produccionEdit = null;
          this.mensaje = 'Producción actualizada exitosamente';
        },
        error: (err) => {
          console.error('Error detallado:', err);
          this.error = 'Error al actualizar producción: ' + (err.error?.detail || err.message || JSON.stringify(err.error) || 'Verifique los datos');
        }
      });
    }
  }

  eliminarProduccion(id: number) {
    if (confirm('¿Está seguro de eliminar este registro de producción?')) {
      this.mensaje = '';
      this.error = '';
      this.apiService.deleteProduccion(id).subscribe({
        next: () => {
          this.cargarProducciones();
          this.mensaje = 'Producción eliminada exitosamente';
        },
        error: (err) => {
          this.error = 'Error al eliminar producción';
        }
      });
    }
  }
}