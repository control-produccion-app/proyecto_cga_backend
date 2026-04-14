import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  stats = {
    totalClientes: 0,
    totalProductos: 0,
    pedidosHoy: 0,
    produccionHoy: 0
  };
  cargando = false;
  error = '';

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.loadStats();
  }

  loadStats() {
    this.cargando = true;
    this.error = '';
    
    // Cargar clientes
    this.apiService.getClientes().subscribe({
      next: (data) => {
        this.stats.totalClientes = Array.isArray(data) ? data.length : data.count || 0;
      },
      error: (err) => {
        if (err.status !== 401) { // 401 ya es manejado por el interceptor
          this.error = 'Error al cargar clientes';
        }
      }
    });

    // Cargar productos
    this.apiService.getProductos().subscribe({
      next: (data) => {
        this.stats.totalProductos = Array.isArray(data) ? data.length : data.count || 0;
      },
      error: (err) => {
        if (err.status !== 401) {
          this.error = 'Error al cargar productos';
        }
      }
    });

    // Cargar pedidos de hoy
    this.apiService.getPedidos().subscribe({
      next: (data) => {
        const pedidos = Array.isArray(data) ? data : data.results || data;
        const hoy = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
        this.stats.pedidosHoy = pedidos.filter((p: any) => p.fecha_pedido?.startsWith(hoy)).length;
      },
      error: (err) => {
        if (err.status !== 401) {
          this.error = 'Error al cargar pedidos';
        }
      }
    });

    // Cargar producción total
    this.apiService.getProducciones().subscribe({
      next: (data) => {
        const produccion = Array.isArray(data) ? data : data.results || data;
        this.stats.produccionHoy = produccion.length;
        this.cargando = false;
      },
      error: (err) => {
        if (err.status !== 401) {
          this.error = 'Error al cargar producción';
        }
        this.cargando = false;
      }
    });
  }
}