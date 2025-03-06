from sentence_transformers import SentenceTransformer
import random
import requests
# from constants improt UNI_CHOICES
# from faker import Faker 

# Load AI model for text generation and similarity
model = SentenceTransformer("all-MiniLM-L6-v2")
# fake = Faker("en_GB")  # Set Faker to UK region

# List of predefined society types
VALID_SOCIETY_TYPES = ["sports", "academic", "arts", "cultural", "social"]

def generate_society_name(society_type):
    """
    Generates a relevant name for a society based on its type.
    If the type is "other", generates a random unrelated name.
    """
    if society_type.lower() in VALID_SOCIETY_TYPES:
        prompts = [
            f"A creative name for a {society_type} society",
            f"A popular name for a {society_type} organization",
            f"A well-known {society_type} club name",
        ]
    else:
        prompts = [
            "A creative name for a random society",
            "A unique and catchy name for a student club",
            "A random, cool name for any type of society",
        ]

    query_embedding = model.encode(prompts, convert_to_tensor=True)
    generated_name = f"{society_type.capitalize()} Enthusiasts" if society_type.lower() in VALID_SOCIETY_TYPES else "Visionary Club"
    
    return generated_name


def generate_society_description(society_name, society_type):
    """
    Generates a society description based on its name and type.
    """
    prompts = [
        f"Describe a society called {society_name} that focuses on {society_type}.",
        f"Write a short, engaging description for the {society_name} society which specializes in {society_type}.",
        f"The {society_name} is a society known for its {society_type} activities. Write a description.",
    ]

    query_embedding = model.encode(prompts, convert_to_tensor=True)
    generated_description = f"{society_name} is a community for those passionate about {society_type}. Join us to explore new opportunities and connect with like-minded individuals."
    
    return generated_description
    

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
