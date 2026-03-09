from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

DEMO_USERS = [
    {
        "username": "demo",
        "password": "demo1234",
        "email": "demo@ailearninghub.ch",
        "first_name": "Gina",
        "last_name": "M.",
        "profile": {"xp": 0, "level": 1, "avatar_color": "#00A76F"},
    },
    {
        "username": "anna",
        "password": "anna1234",
        "email": "anna@ailearninghub.ch",
        "first_name": "Anna",
        "last_name": "M.",
        "profile": {"xp": 520, "level": 5, "avatar_color": "#8E33FF"},
    },
    {
        "username": "marco",
        "password": "marco1234",
        "email": "marco@ailearninghub.ch",
        "first_name": "Marco",
        "last_name": "L.",
        "profile": {"xp": 410, "level": 4, "avatar_color": "#00B8D9"},
    },
]


class Command(BaseCommand):
    help = "Create demo users for the AI Learning Hub"

    def handle(self, *args, **options):
        for data in DEMO_USERS:
            profile_data = data.pop("profile")
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "email": data["email"],
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                },
            )
            if created:
                user.set_password(data["password"])
                user.save()

            # Update profile (created automatically by signal)
            profile = user.profile
            for key, value in profile_data.items():
                setattr(profile, key, value)
            profile.save()

            # Restore for re-runnability within same process
            data["profile"] = profile_data

            action = "Created" if created else "Updated"
            self.stdout.write(f"  {action} user: {data['username']}")

        self.stdout.write(self.style.SUCCESS("Demo users created successfully!"))
