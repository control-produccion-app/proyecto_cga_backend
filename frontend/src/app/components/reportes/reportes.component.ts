import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-reportes',
  templateUrl: './reportes.component.html',
  styleUrls: ['./reportes.component.css']
})
export class ReportesComponent implements OnInit {
  insumoId = 1;
  stockInfo: any = null;
  insumosList: any[] = [];
  cargando = false;
  error = '';

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.cargarInsumos();
  }

  cargarInsumos() {
    this.cargando = true;
    this.apiService.getInsumos().subscribe({
      next: (data) => {
        this.insumosList = Array.isArray(data) ? data : data.results || data;
        if (this.insumosList.length > 0) {
          this.insumoId = this.insumosList[0].id_insumo;
        }
        this.cargando = false;
      },
      error: (err) => {
        this.error = 'Error al cargar insumos';
        this.cargando = false;
      }
    });
  }

  consultarStock() {
    this.stockInfo = null;
    this.error = '';
    this.apiService.getStockInsumo(this.insumoId).subscribe({
      next: (data) => {
        this.stockInfo = data;
      },
      error: (err) => {
        console.error('Error consultando stock:', err);
        this.error = 'Error al consultar stock: ' + (err.error?.detail || err.message || 'Error del servidor');
      }
    });
  }
}