import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { Cliente } from '../../models/cliente.model';

@Component({
  selector: 'app-clientes',
  templateUrl: './clientes.component.html',
  styleUrls: ['./clientes.component.css']
})
export class ClientesComponent implements OnInit {
  clientes: Cliente[] = [];
  clienteEdit: Cliente | null = null;
  nuevoCliente: Partial<Cliente> = {};
  mostrarForm = false;
  mensaje = '';
  error = '';
  cargando = false;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.cargarClientes();
  }

  cargarClientes() {
    this.cargando = true;
    this.apiService.getClientes().subscribe({
      next: (data) => {
        this.clientes = Array.isArray(data) ? data : data.results || data;
        this.cargando = false;
      },
      error: (err) => {
        if (err.status !== 401) {
          this.error = 'Error al cargar clientes';
        }
        this.cargando = false;
      }
    });
  }

  crearCliente() {
    this.mensaje = '';
    this.error = '';
    console.log('Datos del cliente a enviar:', this.nuevoCliente);
    this.apiService.createCliente(this.nuevoCliente).subscribe({
      next: (response) => {
        console.log('Respuesta del servidor:', response);
        this.cargarClientes();
        this.nuevoCliente = {};
        this.mostrarForm = false;
        this.mensaje = 'Cliente creado exitosamente';
      },
      error: (err) => {
        console.error('Error creando cliente:', err);
        console.error('Detalles del error:', err.error);
        if (err.status === 401) {
          // El interceptor ya maneja la redirección
          return;
        }
        if (err.error && err.error.detail) {
          this.error = `Error: ${err.error.detail}`;
        } else if (err.error && typeof err.error === 'object') {
          const errors = Object.values(err.error).flat();
          this.error = `Error: ${errors.join(', ')}`;
        } else {
          this.error = 'Error al crear cliente';
        }
      }
    });
  }

  editarCliente(cliente: Cliente) {
    this.clienteEdit = { ...cliente };
  }

  actualizarCliente() {
    if (this.clienteEdit) {
      this.mensaje = '';
      this.error = '';
      this.apiService.updateCliente(this.clienteEdit.id_cliente, this.clienteEdit).subscribe({
        next: () => {
          this.cargarClientes();
          this.clienteEdit = null;
          this.mensaje = 'Cliente actualizado exitosamente';
        },
        error: (err) => {
          this.error = 'Error al actualizar cliente';
        }
      });
    }
  }

  eliminarCliente(id: number) {
    if (confirm('¿Está seguro de eliminar este cliente?')) {
      this.mensaje = '';
      this.error = '';
      this.apiService.deleteCliente(id).subscribe({
        next: () => {
          this.cargarClientes();
          this.mensaje = 'Cliente eliminado exitosamente';
        },
        error: (err) => {
          this.error = 'Error al eliminar cliente';
        }
      });
    }
  }
}