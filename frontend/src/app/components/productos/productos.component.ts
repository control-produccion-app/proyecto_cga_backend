import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { Producto } from '../../models/producto.model';

@Component({
  selector: 'app-productos',
  templateUrl: './productos.component.html',
  styleUrls: ['./productos.component.css']
})
export class ProductosComponent implements OnInit {
  productos: Producto[] = [];
  productoEdit: Producto | null = null;
  nuevoProducto: Partial<Producto> = {
    unidad_venta_base: 'KILO'
  };
  tiposProduccion: any[] = [];
  mostrarForm = false;
  mensaje = '';
  error = '';
  cargando = false;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.cargarProductos();
    this.cargarTiposProduccion();
  }

  cargarProductos() {
    this.cargando = true;
    this.apiService.getProductos().subscribe({
      next: (data) => {
        this.productos = Array.isArray(data) ? data : data.results || data;
        this.cargando = false;
      },
      error: (err) => {
        this.error = 'Error al cargar productos';
        this.cargando = false;
      }
    });
  }

  cargarTiposProduccion() {
    this.apiService.getTiposProduccion().subscribe({
      next: (data) => {
        this.tiposProduccion = Array.isArray(data) ? data : data.results || data;
      },
      error: (err) => {
        console.error('Error al cargar tipos de producción', err);
      }
    });
  }

  getTipoProduccionNombre(id: number): string {
    const tipo = this.tiposProduccion.find(t => t.id_tipo_produccion === id);
    return tipo ? tipo.nombre : id;
  }

  crearProducto() {
    this.mensaje = '';
    this.error = '';
    this.apiService.createProducto(this.nuevoProducto).subscribe({
      next: () => {
        this.cargarProductos();
        this.nuevoProducto = {};
        this.mostrarForm = false;
        this.mensaje = 'Producto creado exitosamente';
      },
      error: (err) => {
        this.error = 'Error al crear producto';
      }
    });
  }

  editarProducto(producto: Producto) {
    this.productoEdit = { ...producto };
  }

  actualizarProducto() {
    if (this.productoEdit) {
      this.mensaje = '';
      this.error = '';
      this.apiService.updateProducto(this.productoEdit.id_producto, this.productoEdit).subscribe({
        next: () => {
          this.cargarProductos();
          this.productoEdit = null;
          this.mensaje = 'Producto actualizado exitosamente';
        },
        error: (err) => {
          this.error = 'Error al actualizar producto';
        }
      });
    }
  }

  eliminarProducto(id: number) {
    if (confirm('¿Está seguro de eliminar este producto?')) {
      this.mensaje = '';
      this.error = '';
      this.apiService.deleteProducto(id).subscribe({
        next: () => {
          this.cargarProductos();
          this.mensaje = 'Producto eliminado exitosamente';
        },
        error: (err) => {
          this.error = 'Error al eliminar producto';
        }
      });
    }
  }
}