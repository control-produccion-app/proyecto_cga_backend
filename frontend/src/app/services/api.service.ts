import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // Turnos
  getTurnos(): Observable<any> {
    return this.http.get(`${this.baseUrl}/turnos/`);
  }

  // Distribuciones
  getDistribuciones(): Observable<any> {
    return this.http.get(`${this.baseUrl}/distribuciones/`);
  }

  // Jornadas
  getJornadas(): Observable<any> {
    return this.http.get(`${this.baseUrl}/jornadas/`);
  }

  // Tipos de producción
  getTiposProduccion(): Observable<any> {
    return this.http.get(`${this.baseUrl}/tipos-produccion/`);
  }

  // Insumos
  getInsumos(): Observable<any> {
    return this.http.get(`${this.baseUrl}/insumos/`);
  }

  // Clientes
  getClientes(): Observable<any> {
    return this.http.get(`${this.baseUrl}/clientes/`);
  }

  getCliente(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/clientes/${id}/`);
  }

  createCliente(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/clientes/`, data);
  }

  updateCliente(id: number, data: any): Observable<any> {
    return this.http.put(`${this.baseUrl}/clientes/${id}/`, data);
  }

  deleteCliente(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/clientes/${id}/`);
  }

  getSaldoCliente(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/clientes/${id}/saldo/`);
  }

  // Productos
  getProductos(): Observable<any> {
    return this.http.get(`${this.baseUrl}/productos/`);
  }

  getProducto(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/productos/${id}/`);
  }

  createProducto(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/productos/`, data);
  }

  updateProducto(id: number, data: any): Observable<any> {
    return this.http.put(`${this.baseUrl}/productos/${id}/`, data);
  }

  deleteProducto(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/productos/${id}/`);
  }

  // Pedidos
  getPedidos(): Observable<any> {
    return this.http.get(`${this.baseUrl}/pedidos/`);
  }

  getPedido(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/pedidos/${id}/`);
  }

  createPedido(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/pedidos/`, data);
  }

  updatePedido(id: number, data: any): Observable<any> {
    return this.http.put(`${this.baseUrl}/pedidos/${id}/`, data);
  }

  deletePedido(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/pedidos/${id}/`);
  }

  // Producción
  getProducciones(): Observable<any> {
    return this.http.get(`${this.baseUrl}/producciones/`);
  }

  getProduccion(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/producciones/${id}/`);
  }

  createProduccion(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/producciones/`, data);
  }

  updateProduccion(id: number, data: any): Observable<any> {
    return this.http.put(`${this.baseUrl}/producciones/${id}/`, data);
  }

  deleteProduccion(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/producciones/${id}/`);
  }

  // Movimientos
  getMovimientos(): Observable<any> {
    return this.http.get(`${this.baseUrl}/movimientos/`);
  }

  getMovimiento(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/movimientos/${id}/`);
  }

  createMovimiento(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/movimientos/`, data);
  }

  updateMovimiento(id: number, data: any): Observable<any> {
    return this.http.put(`${this.baseUrl}/movimientos/${id}/`, data);
  }

  deleteMovimiento(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/movimientos/${id}/`);
  }

  getResumenJornada(jornadaId: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/movimientos/resumen_jornada/?jornada_id=${jornadaId}`);
  }

  // Bodega
  getMovimientosBodega(): Observable<any> {
    return this.http.get(`${this.baseUrl}/movimientos-bodega/`);
  }

  getMovimientoBodega(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/movimientos-bodega/${id}/`);
  }

  createMovimientoBodega(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/movimientos-bodega/`, data);
  }

  updateMovimientoBodega(id: number, data: any): Observable<any> {
    return this.http.put(`${this.baseUrl}/movimientos-bodega/${id}/`, data);
  }

  deleteMovimientoBodega(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/movimientos-bodega/${id}/`);
  }

  // Reportes
  getStockInsumo(insumoId: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/reportes/stock_insumo/?insumo_id=${insumoId}`);
  }
}