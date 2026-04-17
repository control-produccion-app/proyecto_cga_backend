from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.db import connection
from api.models import Turno, Distribucion

class Command(BaseCommand):
    help = 'Carga datos iniciales de Turno y Distribución según especificación del proyecto'
    
    def handle(self, *args, **options):
        # Datos para Turno
        turnos_data = [
            {'id_turno': 1, 'nombre_turno': 'Madrugada'},
            {'id_turno': 2, 'nombre_turno': 'Mañana'},
            {'id_turno': 3, 'nombre_turno': 'Tarde'},
        ]
        
        for turno_data in turnos_data:
            turno, created = Turno.objects.update_or_create(
                id_turno=turno_data['id_turno'],
                defaults={'nombre_turno': turno_data['nombre_turno']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Turno creado: {turno.nombre_turno}'))
            else:
                self.stdout.write(self.style.WARNING(f'Turno actualizado: {turno.nombre_turno}'))
        
        # Datos para Distribución
        distribuciones_data = [
            {'id_distribucion': 1, 'nombre_distribucion': 'Repartidor 1'},
            {'id_distribucion': 2, 'nombre_distribucion': 'Repartidor 2'},
            {'id_distribucion': 3, 'nombre_distribucion': 'Retiro en panadería'},
            {'id_distribucion': 4, 'nombre_distribucion': 'Sala de ventas'},
        ]
        
        for dist_data in distribuciones_data:
            distribucion, created = Distribucion.objects.update_or_create(
                id_distribucion=dist_data['id_distribucion'],
                defaults={'nombre_distribucion': dist_data['nombre_distribucion']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Distribución creada: {distribucion.nombre_distribucion}'))
            else:
                self.stdout.write(self.style.WARNING(f'Distribución actualizada: {distribucion.nombre_distribucion}'))
        
        # Crear grupos de roles del sistema
        grupos_data = [
            'Administrador',
            'JefeProduccion',
            'Vendedor',
            'Bodeguero'
        ]
        
        for nombre_grupo in grupos_data:
            grupo, created = Group.objects.get_or_create(name=nombre_grupo)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Grupo creado: {nombre_grupo}'))
            else:
                self.stdout.write(self.style.WARNING(f'Grupo ya existente: {nombre_grupo}'))
        
        # Sincronizar secuencias de PostgreSQL después de inserciones con IDs fijos
        try:
            with connection.cursor() as cursor:
                # Sincronizar secuencia de turno
                cursor.execute("SELECT setval('turno_id_turno_seq', (SELECT MAX(id_turno) FROM turno))")
                self.stdout.write(self.style.SUCCESS('Secuencia de turno sincronizada'))
                
                # Sincronizar secuencia de distribucion
                cursor.execute("SELECT setval('distribucion_id_distribucion_seq', (SELECT MAX(id_distribucion) FROM distribucion))")
                self.stdout.write(self.style.SUCCESS('Secuencia de distribución sincronizada'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al sincronizar secuencias: {e}'))
        
        self.stdout.write(self.style.SUCCESS('Datos iniciales cargados exitosamente'))
