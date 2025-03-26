import os
import sys
import django
import random
from faker import Faker
from django.conf import settings
import constants
from ai_seed import generate_society_description, generate_society_name 
from ai_seed import generate_event_location
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta

# Set up the project base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.users.models import CustomUser
from apps.societies.models import Society, Membership, MembershipRole, MembershipStatus
from apps.events.models import Event, EventRegistration
from apps.news.models import News


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

def get_location_from_email(email):
    """Extracts university abbreviation from email and finds the corresponding city."""
    abb = email.split("@")[-1].split(".")[0]  # Extract 'abb' from email
    for city, universities in constants.UNI_CHOICES.items():
        if abb in universities:
            return city
    return "Unknown"  # Default if no match is found

def create_dummy_societies(users, n=50):
    """Creates n dummy societies with AI-generated names and descriptions."""
    societies = []
    existing_names = set(Society.objects.values_list("name", flat=True))  # Track unique names

    for _ in range(n):
        society_type = random.choice([key for key, _ in constants.SOCIETY_TYPE_CHOICES])
        

        generated_name = generate_society_name(society_type, existing_names)
        existing_names.add(generated_name)


        generated_description = generate_society_description(generated_name, society_type,)

        if random.random() < 0.7: 
            fee = 0
        else:
            fee = random.randint(1, 20)  
            
        society = Society.objects.create(
            name=generated_name,
            description=generated_description,
            society_type=society_type,
            status=random.choice([key for key, _ in constants.SOCIETY_STATUS_CHOICES]),
            manager=random.choice(users),
            joining_fee = fee
            
        )

        society.location = get_location_from_email(society.manager.email)  # Get location from email

        if society.status == "approved" or society.status == "request_delete" :
            society.members.set(random.sample(users, random.randint(1, len(users))))
        if society.status == "approved":
            society.visibility = "Public"
        society.save() 
        societies.append(society)

    return societies


LAT_MIN, LAT_MAX = 49.9, 60.9
LON_MIN, LON_MAX = -8.6, 1.8

def random_location_cord():
    """영국 내 랜덤 위도, 경도 반환"""
    return round(random.uniform(LAT_MIN, LAT_MAX), 6), round(random.uniform(LON_MIN, LON_MAX), 6)

def create_dummy_events(societies, n=70):
    """Creates n dummy events linked to random societies with updated attributes."""
    events = []
    for _ in range(n):
        city = random.choice(list(constants.UNI_CHOICES.keys()))
        location = generate_event_location(city)
        latitude, longitude = random_location_cord()


        # Generate future datetime with timezone awareness
        future_date = fake.future_datetime()
        if timezone.is_naive(future_date):
            future_date = timezone.make_aware(future_date)

        is_free = random.choice([True, False])  # Determine if the event is free
        fee = 0.00 if is_free else round(random.randint(5, 100), 2)

        event = Event.objects.create(
            event_type=random.choice([key for key in constants.EVENT_TYPE_CHOICES]),
            name=fake.sentence(nb_words=5),
            location=location,
            date=future_date,  # Use timezone-aware datetime
            keyword=fake.word(),
            is_free=is_free,  # ✅ Store if event is free
            fee=fee,  
            member_only=random.choice([True, False]),
            capacity=random.randint(10, 500),
            start_time=fake.time_object(),
            end_time=fake.time_object(),
            latitude=latitude,  # 랜덤 위도 값
            longitude=longitude,  # 랜덤 경도 값
        )

        approved_societies = [s for s in societies if s.status == "approved"]

        if approved_societies:
            event.society.set(random.sample(approved_societies, random.randint(1, min(3, len(approved_societies)))))

        events.append(event)
    return events

def create_dummy_news (events):
    fake_news_entries = []

    for event in events:  # Creating 20 fake news entries

        news_entry = News(
            title=event.name,
            content=f"New {event.name} event!\nHosted by {', '.join([s.name for s in event.society.all()])}\nOn {event.date}",
            date_posted=now() - timedelta(days=random.randint(1, 30)),
            views=random.randint(0, 100),
            is_published=True
        )
        fake_news_entries.append(news_entry)

    # **Step 1: Bulk create News objects (now they have IDs)**
    created_news = News.objects.bulk_create(fake_news_entries)

    # **Step 2: Link the ManyToMany relationships**
    for news_entry, event in zip(created_news, events):
        news_entry.society.set(event.society)

    return created_news


def create_dummy_event_registrations(users, events, n=20):
    """Creates dummy event registrations."""
    for _ in range(n):
        EventRegistration.objects.create(
            event=random.choice(events),
            user=random.choice(users),
            status=random.choice(["accepted", "waitlisted", "rejected"]),
        )

def create_dummy_memberships(users, societies):
    """Creates Membership records for users in societies."""
    memberships = []
    for society in societies:
        members = random.sample(users, random.randint(1, min(10, len(users))))  # Assign 1-10 random members
        for user in members:
            membership = Membership(
                user=user,
                society=society,
                role=random.choice([MembershipRole.MEMBER, MembershipRole.CO_MANAGER]),
                status=MembershipStatus.APPROVED,  # Ensure they are approved members
            )
            memberships.append(membership)

    Membership.objects.bulk_create(memberships)  # Bulk insert for efficiency
    print(f"Created {len(memberships)} memberships.")

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

    #  Generate Members
    create_dummy_memberships(users, societies)
    print("Dummy memberships registrations created.")

    # Generate events
    events = create_dummy_events(societies, 30)
    print(f"Created {len(events)} events.")

    news = create_dummy_news(events)
    print(f"Created {len(news)} news.")

    # Generate event registrations
    create_dummy_event_registrations(users, events, 40)
    print("Dummy event registrations created.")

    print("Seeding complete!")


'''
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
                is_published=True
            )
        )

    # Bulk create for efficiency
    News.objects.bulk_create(fake_news_entries)

    print(f"Successfully created {len(fake_news_entries)} fake news articles!")

# Call the function when seeding
# create_fake_news()
'''