from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed all demo data (lessons, achievements, users)"

    def handle(self, *args, **options):
        self.stdout.write("Seeding lessons and achievements...")
        call_command("seed_lessons", stdout=self.stdout)

        self.stdout.write("\nSeeding demo users...")
        call_command("seed_users", stdout=self.stdout)

        self.stdout.write(self.style.SUCCESS("\nAll seed data created!"))
