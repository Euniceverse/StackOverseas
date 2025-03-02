import os
import sys
import django
import random
from faker import Faker
from django.conf import settings
import constants

# Set up the project base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.users.models import CustomUser
from apps.societies.models import Society
from apps.events.models import Event, EventRegistration


def random_location():
    city = random.choice(list(constants.UNI_CHOICES.keys()))
    while city == "Online":
        city = random.choice(list(constants.UNI_CHOICES.keys()))
    return city

def create_superuser():
    """Creates a default superuser if one doesn't exist."""
    User = CustomUser  # Your custom user model
    
    superuser_email = "admin@example.ac.uk"
    
    if not User.objects.filter(email=superuser_email).exists():
        User.objects.create_superuser(
            email=superuser_email,
            first_name="Admin",
            last_name="User",
            preferred_name="Admin",
            password="password123"  # Change this to a secure password
        )
        print("Superuser created successfully!")
    else:
        print("Superuser already exists, skipping creation.")



# Initialize Faker
fake = Faker()

def generate_unique_email(first_name, last_name):
    first_name = first_name.lower()
    last_name = last_name.lower()

    # Choose a random uni
    city = random_location()
    university = random.choice(constants.UNI_CHOICES[city])

    base_email = f"{first_name}.{last_name}@{university}.ac.uk"
    email = base_email
    counter = 1

    # Check if email exists in the database and generate a unique one
    while CustomUser.objects.filter(email=email).exists():
        email = f"{first_name}.{last_name}{counter}@{city}.ac.uk"
        counter += 1

    return email

def create_dummy_users(n=100):
    """Creates n dummy users with updated attributes."""
    users = []
    for _ in range(n):
        fake_first_name=fake.first_name()
        fake_last_name=fake.last_name()

        user = CustomUser.objects.create_user(
            first_name=fake_first_name,
            last_name=fake_last_name,
            email= generate_unique_email(fake_first_name, fake_last_name), # type: ignore
            preferred_name=fake_first_name+"y",
            password="password123",
        )
        # user.is_active=True  # Ensure user is active by default
        users.append(user)
    return users



def create_dummy_societies(users, n=50):
    """Creates n dummy societies with random users as managers and members."""
    societies = []
    for _ in range(n):
        society = Society.objects.create(
            name=fake.unique.company(),
            description=fake.text(),
            society_type = random.choice([key for key, _ in constants.SOCIETY_TYPE_CHOICES]),
            status=random.choice([key for key, _ in constants.SOCIETY_STATUS_CHOICES]),
            manager=random.choice(users),
            # members_count=random.randint(1, 10)  # Assign random members count
        )
        if society.status == "approved":
            society.members.set(random.sample(users, random.randint(1, len(users))))  # Assign random members
        societies.append(society)
    return societies




def create_dummy_events(societies, n=70):
    """Creates n dummy events linked to random societies with updated attributes."""
    events = []
    for _ in range(n):
        event = Event.objects.create(
            event_type=random.choice([key for key in constants.EVENT_TYPE_CHOICES]),
            name=fake.sentence(nb_words=5),
            location= random_location,
            date=fake.future_datetime(),
            keyword=fake.word(),
            is_free=random.choice([True, False]),
            member_only=random.choice([True, False]),
            capacity=random.randint(10, 500),
            start_time=fake.time_object(),
            end_time=fake.time_object()
        )

        approved_societies = [s for s in societies if s.status == "approved"]

        if approved_societies:  # Ensure there's at least one approved society
            event.society.set(random.sample(approved_societies, random.randint(1, min(3, len(approved_societies)))))

        # event.society.set(random.sample(societies, random.randint(1, 3)))  # Select 1 to 3 societies

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

    # Generate superuser
    create_superuser()

    # Generate users
    users = create_dummy_users(50)
    print(f"Created {len(users)} users.")

    # Generate societies
    societies = create_dummy_societies(users, 50)
    print(f"Created {len(societies)} societies.")

    # Generate events
    events = create_dummy_events(societies, 30)
    print(f"Created {len(events)} events.")

    # Generate event registrations
    create_dummy_event_registrations(users, events, 40)
    print("Dummy event registrations created.")

    print("Seeding complete!")


from django.utils.timezone import now
import random
from datetime import timedelta
from apps.news.models import News
from apps.societies.models import Society

def create_fake_news():
    # Fetch only approved societies from the seed data
    approved_societies = list(Society.objects.filter(status="approved"))

    if not approved_societies:
        print("No approved societies found. Fake news will not be created.")
        return

    # Clear old fake news before seeding new ones
    News.objects.all().delete()

    # Generate 20 fake news articles linked to seeded societies
    fake_news_entries = []
    for i in range(20):  # Creating 20 fake news entries
        society = random.choice(approved_societies)  # Ensure news belongs to a seeded society

        fake_news_entries.append(
            News(
                title=f"Test News {i+1}",
                content="This is a test news content for filtering and sorting.",
                date_posted=now() - timedelta(days=random.randint(1, 30)),
                views=random.randint(0, 100),  # Randomized views for popularity sorting
                society=society,  # Properly linking to an approved seeded society
            )
        )

    # Bulk create for efficiency
    News.objects.bulk_create(fake_news_entries)

    print(f"Successfully created {len(fake_news_entries)} fake news articles!")

# Call the function when seeding
create_fake_news()
