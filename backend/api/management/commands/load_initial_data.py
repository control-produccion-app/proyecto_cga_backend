from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import connection

from api.models import Turno, Distribucion


class Command(BaseCommand):
    help = "Carga datos base mÃ­nimos del sistema"

    def handle(self, *args, **options):
        self.crear_roles()
        self.crear_turnos()
        self.crear_distribuciones()
        self.sincronizar_secuencias()

        self.stdout.write(
            self.style.SUCCESS("Datos base cargados correctamente.")
        )

    def crear_roles(self):
        roles = [
            "Administrador",
            "Encargado de turno",
        ]

        for nombre_rol in roles:
            grupo, creado = Group.objects.get_or_create(name=nombre_rol)

            if creado:
                self.stdout.write(
                    self.style.SUCCESS(f"Rol creado: {grupo.name}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Rol ya existÃ­a: {grupo.name}")
                )

    def crear_turnos(self):
        turnos = [
            {"id_turno": 1, "nombre_turno": "Madrugada"},
            {"id_turno": 2, "nombre_turno": "MaÃ±ana"},
            {"id_turno": 3, "nombre_turno": "Tarde"},
        ]

        for datos_turno in turnos:
            turno, creado = Turno.objects.update_or_create(
                id_turno=datos_turno["id_turno"],
                defaults={"nombre_turno": datos_turno["nombre_turno"]},
            )

            if creado:
                self.stdout.write(
                    self.style.SUCCESS(f"Turno creado: {turno.nombre_turno}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Turno actualizado: {turno.nombre_turno}")
                )

    def crear_distribuciones(self):
        distribuciones = [
            {"id_distribucion": 1, "nombre_distribucion": "Ricardo"},
            {"id_distribucion": 2, "nombre_distribucion": "Osvaldo"},
            {"id_distribucion": 3, "nombre_distribucion": "Retiro Panaderia"},
        ]

        for datos_distribucion in distribuciones:
            distribucion, creado = Distribucion.objects.update_or_create(
                id_distribucion=datos_distribucion["id_distribucion"],
                defaults={
                    "nombre_distribucion": datos_distribucion["nombre_distribucion"]
                },
            )

            if creado:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"DistribuciÃ³n creada: {distribucion.nombre_distribucion}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"DistribuciÃ³n actualizada: {distribucion.nombre_distribucion}"
                    )
                )

    def sincronizar_secuencias(self):
        if connection.vendor != "postgresql":
            self.stdout.write(
                self.style.WARNING(
                    "SincronizaciÃ³n de secuencias omitida: no es PostgreSQL."
                )
            )
            return

        secuencias = [
            ("turno", "id_turno"),
            ("distribucion", "id_distribucion"),
        ]

        with connection.cursor() as cursor:
            for tabla, columna in secuencias:
                cursor.execute(
                    f"""
                    SELECT setval(
                        pg_get_serial_sequence(%s, %s),
                        COALESCE((SELECT MAX({columna}) FROM {tabla}), 1),
                        true
                    );
                    """,
                    [tabla, columna],
                )

        self.stdout.write(
            self.style.SUCCESS("Secuencias base sincronizadas.")
        )
