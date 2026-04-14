import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { Pedido } from '../../models/pedido.model';

@Component({
  selector: 'app-pedidos',
  templateUrl: './pedidos.component.html',
  styleUrls: ['./pedidos.component.css']
})
export class PedidosComponent implements OnInit {
  pedidos: Pedido[] = [];
  pedidoEdit: Pedido | null = null;
  nuevoPedido: Partial<Pedido> = {
    fecha_pedido: new Date().toISOString().split('T')[0],
    fecha_entrega_solicitada: new Date().toISOString().split('T')[0]
  };
  mostrarForm = false;
  mensaje = '';
  error = '';
  cargando = false;
  clientesList: any[] = [];
  distribucionesList: any[] = [];
  cargandoListas = false;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.cargarPedidos();
    this.cargarListas();
  }

  cargarPedidos() {
    this.cargando = true;
    this.apiService.getPedidos().subscribe({
      next: (data) => {
        this.pedidos = Array.isArray(data) ? data : data.results || data;
        this.cargando = false;
      },
      error: (err) => {
        this.error = 'Error al cargar pedidos';
        this.cargando = false;
      }
    });
  }

  cargarListas() {
    this.cargandoListas = true;
    this.apiService.getClientes().subscribe({
      next: (data) => {
        this.clientesList = Array.isArray(data) ? data : data.results || data;
        this.apiService.getDistribuciones().subscribe({
          next: (distData) => {
            this.distribucionesList = Array.isArray(distData) ? distData : distData.results || distData;
            this.cargandoListas = false;
          },
          error: (err) => {
            this.error = 'Error al cargar distribuciones';
            this.cargandoListas = false;
          }
        });
      },
      error: (err) => {
        this.error = 'Error al cargar clientes';
        this.cargandoListas = false;
      }
    });
  }

  crearPedido() {
    this.mensaje = '';
    this.error = '';
    this.apiService.createPedido(this.nuevoPedido).subscribe({
      next: () => {
        this.cargarPedidos();
        this.nuevoPedido = {
          fecha_pedido: new Date().toISOString().split('T')[0],
          fecha_entrega_solicitada: new Date().toISOString().split('T')[0]
        };
        this.mostrarForm = false;
        this.mensaje = 'Pedido creado exitosamente';
      },
      error: (err) => {
        this.error = 'Error al crear pedido';
      }
    });
  }

  editarPedido(pedido: Pedido) {
    this.pedidoEdit = { ...pedido };
  }

  actualizarPedido() {
    if (this.pedidoEdit) {
      this.mensaje = '';
      this.error = '';
      this.apiService.updatePedido(this.pedidoEdit.id_pedido, this.pedidoEdit).subscribe({
        next: () => {
          this.cargarPedidos();
          this.pedidoEdit = null;
          this.mensaje = 'Pedido actualizado exitosamente';
        },
        error: (err) => {
          this.error = 'Error al actualizar pedido';
        }
      });
    }
  }

  eliminarPedido(id: number) {
    if (confirm('¿Está seguro de eliminar este pedido?')) {
      this.mensaje = '';
      this.error = '';
      this.apiService.deletePedido(id).subscribe({
        next: () => {
          this.cargarPedidos();
          this.mensaje = 'Pedido eliminado exitosamente';
        },
        error: (err) => {
          this.error = 'Error al eliminar pedido';
        }
      });
    }
  }
}