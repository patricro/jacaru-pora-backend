from django.core.management.base import BaseCommand, CommandError
from django.utils.crypto import get_random_string
from MDS.settings import BASE_DIR
from core.models import User


class Command(BaseCommand):
    help = "Comando para administrar usuarios"

    def add_arguments(self, parser):
        parser_group = parser.add_mutually_exclusive_group(required=True)
        parser_group.add_argument(
            "--users", type=str,
            help="Crea usuarios en forma masiva args : archivo csv, csv args: DNI, Email, Municipio ID, Nombres, Apellido")
        parser_group.add_argument(
            "--superuser", nargs="+",
            help="Crea un super usuario args: DNI, Contraseña, Email, CUIL, Municipio ID, Nombres, Apellido")

    def handle(self, *args, **options):
        try:
            if options["users"]:
                self.create_users(options["users"])
            else:
                self.create_superuser(options["superuser"])

        except CommandError as e:
            self.stdout.write(self.style.ERROR(e))

    def create_users(self, file_pah: str):
        with open(f"{BASE_DIR}/media/out.csv", "w") as out:
            lines = []
            with open(file_pah) as file:
                try:
                    i = 0
                    for i, line in enumerate(file.readlines(), start=1):
                        attrs = line.split(",")
                        password = get_random_string(16)
                        u = User.objects.create_user(
                            attrs[0], attrs[1], password=password,
                            municipio_id=attrs[2], first_name=attrs[3],
                            last_name=attrs[4])
                        lines.append(f"{u.username};{password};\n")

                except Exception:
                    pass

            out.writelines(lines)
            out.close()

        self.stdout.write(self.style.SUCCESS(f"{i} usuario/s creados"))

    def create_superuser(self, attrs: list):
        if len(attrs) != 7:
            self.stdout.write(self.style.ERROR("Se Necesitan minimo 7 argumentos"))
            return

        obj = User.objects.create_superuser(
            username=attrs[0], email=attrs[2], password=attrs[1], cuil=attrs[3], 
            municipio_id=attrs[4], first_name=attrs[5], last_name=attrs[6])
        
        if obj:
            self.stdout.write(self.style.SUCCESS(f"Usuario {obj} creado"))
        else:
            self.stdout.write(self.style.ERROR("Error al crear el usuario"))
