MAX_NAME = 50
MAX_DESCRIPTION = 200
MAX_LOCATION = 255
MAX_KEYWORD = 50
MAX_DIGIT = 10

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
