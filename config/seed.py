import os
import sys
import django
import random
from faker import Faker
from django.conf import settings

# Set up the project base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.users.models import CustomUser
from apps.societies.models import Society
from apps.events.models import Event, EventRegistration
from config.settings import ALLOWED_SOCIETY_TYPES

# Initialize Faker
fake = Faker()

def create_dummy_users(n=10):
    """Creates n dummy users with updated attributes."""
    users = []
    for _ in range(n):
        user = CustomUser.objects.create_user(
            email=fake.email().replace("@example.com", "@uni.ac.uk"),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            preferred_name=fake.first_name(),
            password="password123",
            is_active=True  # Ensure user is active by default
        )
        users.append(user)
    return users

def create_dummy_societies(users, n=5):
    """Creates n dummy societies with random users as managers and members."""
    societies = []
    for _ in range(n):
        society = Society.objects.create(
            name=fake.company(),
            description=fake.text(),
            society_type=random.choice(ALLOWED_SOCIETY_TYPES),
            status=random.choice(["pending", "approved", "rejected"]),
            manager=random.choice(users),
            members_count=random.randint(1, 10)  # Assign random members count
        )
        # society.members.set(random.sample(users, random.randint(1, 10)))  # Assign random members
        societies.append(society)
    return societies

def create_dummy_events(societies, n=10):
    """Creates n dummy events linked to random societies with updated attributes."""
    events = []
    for _ in range(n):
        event = Event.objects.create(
            event_type=random.choice([choice[0] for choice in settings.EVENT_TYPE_CHOICES]),
            society=random.choice(societies),
            name=fake.sentence(nb_words=5),
            location=random.choice(["London", "Manchester", "Online", "Birmingham"]),
            date=fake.future_datetime(),
            keyword=fake.word(),
            is_free=random.choice([True, False]),
            members_only=random.choice([True, False]),
            capacity=random.randint(10, 500),
        )
        events.append(event)
    return events

def create_dummy_event_registrations(users, events, n=20):
    """Creates dummy event registrations."""
    for _ in range(n):
        EventRegistration.objects.create(
            event=random.choice(events),
            user=random.choice(users),
            status=random.choice(["accepted", "waitlisted", "rejected"]),
        )

if __name__ == "__main__":
    print("Generating dummy data...")

    # Generate users
    users = create_dummy_users(10)
    print(f"Created {len(users)} users.")

    # Generate societies
    societies = create_dummy_societies(users, 10)
    print(f"Created {len(societies)} societies.")

    # Generate events
    events = create_dummy_events(societies, 15)
    print(f"Created {len(events)} events.")

    # Generate event registrations
    create_dummy_event_registrations(users, events, 20)
    print("Dummy event registrations created.")

    print("Seeding complete!")
