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
            name=fake.company(),
            description=fake.text(),
            society_type = random.choice([key for key, _ in constants.SOCIETY_TYPE_CHOICES]),
            status=random.choice(["pending", "approved", "rejected"]),
            manager=random.choice(users),
            # members_count=random.randint(1, 10)  # Assign random members count
        )
        if society.status == "approved":
            society.members.set(random.sample(users, random.randint(1, 10)))  # Assign random members
        societies.append(society)
    return societies



import os
import sys
import django
import random
import requests
from faker import Faker
from django.conf import settings

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.societies.models import Society
from apps.events.models import Event

# Initialize Faker
fake = Faker()

import os
import sys
import django
import random
import time
import requests
from faker import Faker
from django.utils.timezone import make_aware

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.societies.models import Society
from apps.events.models import Event

# Initialize Faker
fake = Faker()

# Dictionary to store cached coordinates (reduce API calls)
location_cache = {}

def get_coordinates(address):
    """Fetch latitude & longitude using OpenStreetMap Nominatim API with error handling and caching."""
    if address in location_cache:
        return location_cache[address]  # ✅ Use cached coordinates

    url = f"https://nominatim.openstreetmap.org/search?format=json&q={address},UK"

    try:
        response = requests.get(url, headers={"User-Agent": "my-app"})
        response.raise_for_status()  # Raise HTTP errors (e.g., 429 Too Many Requests)

        data = response.json()  # Convert to JSON safely
        print(f"📍 API response for {address}: {data}")  # ✅ Debugging print

        if data:
            lat, lon = float(data[0]["lat"]), float(data[0]["lon"])
            location_cache[address] = (lat, lon)  # ✅ Cache the coordinates
            time.sleep(1)  # ✅ Delay to prevent API bans
            return lat, lon

    except requests.exceptions.RequestException as e:
        print(f"⚠️ API request failed for {address}: {e}")

    except ValueError as e:
        print(f"⚠️ JSON decode error for {address}: {e}")

    return None, None  # Return None if lookup fails


def create_dummy_events(societies, n=15):
    """Creates n dummy events linked to random societies with real coordinates."""
    events = []

    sample_addresses = [
        "Big Ben, London", "Buckingham Palace, London", "Oxford University, Oxford",
        "Manchester Town Hall, Manchester", "Birmingham Library, Birmingham",
        "Edinburgh Castle, Edinburgh", "Liverpool Cathedral, Liverpool"
    ]

    for _ in range(n):
        address = random.choice(sample_addresses)
        latitude, longitude = get_coordinates(address)  # Fetch real lat/lon

        if latitude is None or longitude is None:
            print(f"❌ Skipping event at {address} (could not fetch coordinates)")
            continue  # Skip event if location lookup failed

        event = Event.objects.create(
            event_type=random.choice(["sports", "music", "academic", "social"]),
            name=fake.sentence(nb_words=5),
            location=address,
            latitude=latitude,
            longitude=longitude,
            date=make_aware(fake.future_datetime()),  # ✅ Convert to timezone-aware datetime
            keyword=fake.word(),
            is_free=random.choice([True, False]),
            member_only=random.choice([True, False]),
            capacity=random.randint(10, 500),
            start_time=fake.time_object(),
            end_time=fake.time_object()
        )

        approved_societies = [s for s in societies if s.status == "approved"]
        if approved_societies:
            event.society.set(random.sample(approved_societies, random.randint(1, min(3, len(approved_societies)))))

        events.append(event)

    return events


if __name__ == "__main__":
    print("🚀 Generating dummy data...")

    # Fetch existing approved societies
    societies = list(Society.objects.filter(status="approved"))

    if not societies:
        print("❌ No approved societies found. Exiting.")
        sys.exit()

    # Delete old events
    Event.objects.all().delete()
    print("🗑️ Old events removed.")

    # Generate new events
    events = create_dummy_events(societies, 15)
    print(f"✅ Created {len(events)} events with valid locations.")

    print("🎉 Dummy data seeding complete!")


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
