MAX_NAME = 50
MAX_DESCRIPTION = 200
MAX_LOCATION = 255
MAX_KEYWORD = 50
MAX_DIGIT = 10

'''class universities:

    # Replace 'your_api_key' with your actual UniDb API key
    api_key = 'your_api_key'
    base_url = 'https://unidbapi.com'

    # Set up the headers with your API key
    headers = {
       'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    # Function to get all universities
    def get_universities():
        endpoint = f'{base_url}/universities'
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f'Error: {response.status_code}')
            return []

    # Fetch universities
    universities = get_universities()
    print(universities)
    locations = []

    # Display university details
    for uni in universities:
        name = uni.get('name')
        city = uni.get('location')  # Assuming 'location' contains the city

        abbreviation = uni.get('abbreviation')  # Assuming there's an 'abbreviation' field
        print(f'Name: {name}, City: {city}, Abbreviation: {abbreviation}')
'''



VISIBILITY_CHOICES = [
    ("Private", "Private"),
    ("Public", "Public"),
]

SOCIETY_TYPE_CHOICES = [
    ("sports", "Sports"),
    ("academic", "Academic"),
    ("arts", "Arts"),
    ("cultural", "Cultural"),
    ("social", "Social"),
    ("other", "Other")
]

# Allowed types of societies
ALLOWED_SOCIETY_TYPES = [
    "Sports",
    "Culture",
    "Langauge",
    "Academia",
    "Games",
    "Arts",
    "Other"
]

EVENT_TYPE_CHOICES = [
    ('sports', 'Sports'),
    ('academic', 'Academic'),
    ('arts', 'Arts'),
    ('cultural', 'Cultural'),
    ('social', 'Social'),
    ('other', 'Other'),
]



REGISTRATION_STATUS_CHOICES = [
    ('accepted', 'Accepted'),
    ('waitlisted', 'Waitlisted'),
    ('rejected', 'Rejected'),
]



UNI_CHOICES = {
    "Online": ["online"],
    "London": ["kcl", "ucl", "imperial", "lse", "qmul"],
    "Manchester": ["uom", "mmu"],
    "Birmingham": ["uob", "bcu", "aston"],
    "Liverpool": ["uol", "ljmu"],
    "Leeds": ["uol", "leedsbeckett"],
    "Sheffield": ["uos", "shu"],
    "Glasgow": ["uog", "strath"],
    "Edinburgh": ["uoe", "hw", "napier"],
    "Bristol": ["uob", "uwe"],
    "Cardiff": ["cardiff", "usw"],
    "Newcastle": ["ncl", "northumbria"],
    "Nottingham": ["uon", "ntu"],
    "Leicester": ["uol", "dmu"],
    "Southampton": ["soton", "solent"],
    "Portsmouth": ["uop"],
    "Coventry": ["coventry", "warwick"],
    "Derby": ["uod"],
    "Stoke-on-Trent": ["staffs", "keele"],
    "Sunderland": ["uos"],
    "Reading": ["uor"],
    "Brighton": ["sussex", "brighton"],
    "Hull": ["hull"],
    "Plymouth": ["plymouth"],
    "Wolverhampton": ["wlv"],
    "Aberdeen": ["abdn", "rgu"],
    "Swansea": ["swansea", "uwtsd"],
    "Milton Keynes": ["ou"],
    "Norwich": ["uea"],
    "Luton": ["beds"],
    "Oxford": ["oxford", "brookes"],
    "Cambridge": ["cam"],
    "York": ["york"],
    "Exeter": ["exeter"],
    "Dundee": ["dundee", "abertay"],
    "Ipswich": ["uos"],
    "Middlesbrough": ["teesside"],
    "Peterborough": ["aru"]
}

SOCIETY_STATUS_CHOICES = [
    ('approved', 'Approved'),
    ('pending', 'Pending'),
    ('rejected', 'Rejected'),
    ('request_delete','Request Delete')
]
# SOC_NAMES = 


