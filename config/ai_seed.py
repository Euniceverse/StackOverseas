from sentence_transformers import SentenceTransformer
import random
import requests
import string

# from constants improt UNI_CHOICES
# from faker import Faker 

# Load AI model for text generation and similarity
model = SentenceTransformer("all-MiniLM-L6-v2")
# fake = Faker("en_GB")  # Set Faker to UK region

# List of predefined society types
# VALID_SOCIETY_TYPES = ["sports", "academic", "arts", "cultural", "social"]

import random
import string

VALID_SOCIETY_TYPES = ["sports", "academic", "arts", "cultural", "social"]

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


# def generate_society_name(society_type, existing_names):
#     """
#     Generates a unique society name using AI, ensuring relevance and diversity.
#     """
#     prompts = [
#         f"Generate a unique and creative name for a {society_type} society.",
#         f"Suggest a professional yet catchy name for a {society_type} club.",
#         f"Come up with a well-known {society_type} organization name.",
#         f"Provide an inspiring name for a {society_type} enthusiasts' group.",
#         f"Suggest a futuristic and appealing name for a {society_type} society.",
#     ]

#     retry_limit = 10  # Prevent infinite loops
#     retries = 0

#     while retries < retry_limit:
#         # Generate AI-based names (assuming ai_model is a proper text generator)
#         generated_name = model.generate_text(random.choice(prompts))

#         # Trim spaces and standardize
#         generated_name = generated_name.strip()

#         if generated_name and generated_name not in existing_names:
#             existing_names.add(generated_name)
#             return generated_name

#         retries += 1

#     # If we fail, generate a fallback name
#     unique_fallback = f"{generated_name} " + ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
#     return unique_fallback


# def generate_society_name(society_type):
#     """
#     Generates a relevant name for a society based on its type.
#     If the type is "other", generates a random unrelated name.
#     """
#     if society_type.lower() in VALID_SOCIETY_TYPES:
#         prompts = [
#             f"A creative name for a {society_type} society",
#             f"A popular name for a {society_type} organization",
#             f"A well-known {society_type} club name",
#         ]
#     else:
#         prompts = [
#             "A creative name for a random society",
#             "A unique and catchy name for a student club",
#             "A random, cool name for any type of society",
#         ]

#     query_embedding = model.encode(prompts, convert_to_tensor=True)
#     generated_name = f"{society_type.capitalize()} Enthusiasts" if society_type.lower() in VALID_SOCIETY_TYPES else "Visionary Club"
    
#     return generated_name


# def generate_society_description(society_name, society_type):
#     """
#     Generates a society description based on its name and type.
#     """
#     prompts = [
#         f"Describe a society called {society_name} that focuses on {society_type}.",
#         f"Write a short, engaging description for the {society_name} society which specializes in {society_type}.",
#         f"The {society_name} is a society known for its {society_type} activities. Write a description.",
#     ]

#     query_embedding = model.encode(prompts, convert_to_tensor=True)
#     generated_description = f"{society_name} is a community for those passionate about {society_type}. Join us to explore new opportunities and connect with like-minded individuals."
    
#     return generated_description
    

# def generate_event_location(city):
#     """
#     Generates a realistic event address based on the given city.
#     If the city is 'Online', it returns 'Online'.
#     """
#     if city.lower() == "online":
#         return "Online"

#     # Generate a realistic address for the given city
#     street = fake.street_name()
#     postcode = fake.postcode()

#     return f"{street}, {city}, {postcode}"

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
