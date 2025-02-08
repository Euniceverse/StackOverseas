MAX_NAME = 50
MAX_DESCRIPTION = 200
MAX_LOCATION = 255

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
    ("Other", "Other")
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