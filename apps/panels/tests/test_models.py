from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

from apps.panels.models import (
    MemberRating, Match, HallOfFame, Comment,
    Gallery, Image, Poll, Question, Option, Vote
)
from apps.societies.models import Society

User = get_user_model()

class PanelsModelsTests(TestCase):
    def setUp(self):
        # Create two users: one to be used as society manager, and another as a regular member.
        self.manager = User.objects.create_user(
            email="manager@example.com",
            first_name="Manager",
            last_name="User",
            preferred_name="Manager",
            password="password123"
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com",
            first_name="User",
            last_name="Two",
            preferred_name="UserTwo",
            password="password123"
        )
        # Create a test society with the manager as its manager.
        self.society = Society.objects.create(
            name="Test Society",
            description="A society for testing panels models.",
            society_type="Test",
            manager=self.manager,
            members_count=2,
        )

    ### MemberRating Tests ###
    def test_member_rating_creation_and_str(self):
        rating = MemberRating.objects.create(
            society=self.society,
            member=self.user2,
            rating=1200
        )
        expected_str = f"{self.user2.first_name} {self.user2.last_name} — 1200 pts"
        self.assertEqual(str(rating), expected_str)

    def test_member_rating_ordering(self):
        rating1 = MemberRating.objects.create(
            society=self.society,
            member=self.user2,
            rating=1200
        )
        rating2 = MemberRating.objects.create(
            society=self.society,
            member=self.manager,
            rating=1300
        )
        ratings = list(MemberRating.objects.filter(society=self.society))
        self.assertEqual(ratings[0], rating2)
        self.assertEqual(ratings[1], rating1)

    ### Match Tests ###
    def test_match_str_method(self):
        match = Match.objects.create(
            society=self.society,
            player1=self.manager,
            player2=self.user2,
            winner=self.manager,
            player1_delta=20,
            player2_delta=-20,
            notes="A test match."
        )
        p1 = f"{self.manager.first_name} {self.manager.last_name}".strip() or self.manager.email
        p2 = f"{self.user2.first_name} {self.user2.last_name}".strip() or self.user2.email
        win = f"{self.manager.first_name} {self.manager.last_name}".strip() if self.manager else 'Draw'
        expected_str = f"{p1} vs {p2} — Winner: {win}"
        self.assertEqual(str(match), expected_str)

    ### HallOfFame Tests ###
    def test_hall_of_fame_creation_and_str(self):
        hof = HallOfFame.objects.create(
            society=self.society,
            member=self.user2,
            season="2025-Q1",
            highest_rating=1400
        )
        name = f"{self.user2.first_name} {self.user2.last_name}".strip() or self.user2.email
        expected_str = f"{name} - 2025-Q1 (1400 pts)"
        self.assertEqual(str(hof), expected_str)

    ### Comment Tests ###
    def test_comment_creation_str_and_likes(self):
        comment = Comment.objects.create(
            society=self.society,
            author=self.manager,
            content="This is a test comment that is sufficiently long."
        )
        comment.likes.add(self.user2)
        expected_str = f"{self.manager.get_full_name()} @ {self.society.name}: {comment.content[:20]}"
        self.assertEqual(str(comment), expected_str)
        self.assertEqual(comment.total_likes(), 1)

    ### Gallery and Image Tests ###
    def test_gallery_creation_and_str(self):
        gallery = Gallery.objects.create(
            title="Test Gallery",
            description="Gallery description.",
            society=self.society
        )
        self.assertEqual(str(gallery), "Test Gallery")

    def test_image_creation_and_str(self):
        test_image = SimpleUploadedFile("test.png", b"file_content", content_type="image/png")
        gallery = Gallery.objects.create(
            title="Test Gallery",
            description="Gallery for testing image.",
            society=self.society
        )
        image = Image.objects.create(
            gallery=gallery,
            image=test_image,
            uploaded_by=self.manager
        )
        self.assertIn("Image in", str(image))
        self.assertIn(gallery.title, str(image))

    ### Poll, Question, Option and Vote Tests ###
    def test_poll_creation_and_str(self):
        poll = Poll.objects.create(
            society=self.society,
            title="Test Poll",
            description="Poll description.",
            deadline=timezone.now() + timedelta(days=7)
        )
        expected_str = f"Test Poll ({self.society.name})"
        self.assertEqual(str(poll), expected_str)
        self.assertFalse(poll.is_closed())

    def test_question_creation_and_str(self):
        poll = Poll.objects.create(
            society=self.society,
            title="Test Poll",
            description="Poll description.",
            deadline=timezone.now() + timedelta(days=7)
        )
        question = Question.objects.create(
            poll=poll,
            question_text="What is your favorite color?"
        )
        self.assertEqual(str(question), "What is your favorite color?")

    def test_option_creation_and_str(self):
        poll = Poll.objects.create(
            society=self.society,
            title="Test Poll",
            description="Poll description.",
            deadline=timezone.now() + timedelta(days=7)
        )
        question = Question.objects.create(
            poll=poll,
            question_text="Favorite color?"
        )
        option = Option.objects.create(
            question=question,
            option_text="Blue",
            option_count=5
        )
        expected_str = f"{question.question_text} - Blue"
        self.assertEqual(str(option), expected_str)

    def test_vote_creation_and_str(self):
        poll = Poll.objects.create(
            society=self.society,
            title="Test Poll",
            description="Poll description.",
            deadline=timezone.now() + timedelta(days=7)
        )
        question = Question.objects.create(
            poll=poll,
            question_text="Favorite color?"
        )
        option = Option.objects.create(
            question=question,
            option_text="Blue",
            option_count=0
        )
        vote = Vote.objects.create(
            option=option,
            voted_by=self.user2
        )
        expected_str = f"{self.user2} voted for {option.option_text}"
        self.assertEqual(str(vote), expected_str)
