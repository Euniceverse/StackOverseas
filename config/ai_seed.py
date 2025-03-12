import random
import requests
import string

from constants import EVENT_TYPE_CHOICES  # Importing the choices from constants

# Extracting only the keys from the list of tuples
VALID_SOCIETY_TYPES = [key for key, _ in EVENT_TYPE_CHOICES]

# Predefined words for society name generation
ADJECTIVES = ["Elite", "Dynamic", "Innovative", "Brilliant", "Visionary", "Prestigious", "Lively", "Energetic"]
NOUNS = {
    "sports": ["Athletes", "Champions", "Runners", "Strikers", "Warriors", "Sportsmen"],
    "academic": ["Scholars", "Thinkers", "Innovators", "Researchers", "Geniuses"],
    "arts": ["Artists", "Creators", "Visionaries", "Designers", "Performers"],
    "cultural": ["Tradition", "Heritage", "Folklore", "Community", "Culturalists"],
    "social": ["Network", "Gathering", "Alliance", "Connectors", "Enthusiasts"],
}

def generate_society_name(society_type, existing_names):
    """
    Generates a unique society name by combining an adjective with a category-specific noun.
    """
    if society_type not in NOUNS:
        society_type = random.choice(list(NOUNS.keys()))  # Fallback if unknown type

    # Generate a name
    while True:
        name = f"{random.choice(ADJECTIVES)} {random.choice(NOUNS[society_type])}"
        
        if name not in existing_names:
            existing_names.add(name)
            return name

    # Fallback if everything fails (should rarely happen)
    return f"{society_type.capitalize()} Club " + ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))

def generate_society_description(society_name, society_type):
    """
    Generates a society description based on its name and type.
    """
    return f"{society_name} is a vibrant society dedicated to {society_type} activities. Join us to learn, grow, and connect with others who share the same passion!"


def generate_event_location(city):
    """
    Generates a real address in the given UK city.
    If the city is 'Online', it returns 'Online'.
    Uses OpenStreetMap (Nominatim) API to fetch real locations.
    """
    if city.lower() == "online":
        return "Online"

    try:
        # Query OpenStreetMap Nominatim for locations in the city
        url = f"https://nominatim.openstreetmap.org/search?city={city}&country=United Kingdom&format=json&limit=5"
        response = requests.get(url, headers={"User-Agent": "StackOverseas-Event-Generator"})
        data = response.json()

        if data:
            location = random.choice(data)  # Pick a random address from results
            address = location.get("display_name", f"{city}, UK")  # Use display name if available
            return address

    except requests.RequestException:
        pass  # In case of an API error, fallback to a random format

    return f"{city}, UK"  # Fallback if no address is found
