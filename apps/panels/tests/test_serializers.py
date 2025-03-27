from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework import serializers

from apps.panels.models import Poll, Question, Option, Vote
from apps.panels.serializers import VoteSerializer, OptionSerializer, QuestionSerializer
from apps.societies.models import Society
from apps.users.models import CustomUser

class SerializersTests(TestCase):
    """Tests for Panel Serializers"""
    def setUp(self):
        # Create a test user to act as manager.
        self.manager = CustomUser.objects.create_user(
            email="manager@example.ac.uk",
            first_name="Manager",
            last_name="User",
            preferred_name="Manager",
            password="password123"
        )
        # Create a test society with the manager.
        self.society = Society.objects.create(
            name="Test Society",
            description="A society for testing serializers.",
            society_type="Test",
            manager=self.manager,
            members_count=1,
        )
        # Create a poll associated with the society.
        self.poll = Poll.objects.create(
            society=self.society,
            title="Test Poll",
            description="Poll for testing",
            deadline=timezone.now() + timedelta(days=7)
        )
        # Create a question associated with the poll.
        self.question = Question.objects.create(
            poll=self.poll,
            question_text="What is your favorite color?"
        )
        # Create two options for the question.
        self.option1 = Option.objects.create(
            question=self.question,
            option_text="Blue",
            option_count=5
        )
        self.option2 = Option.objects.create(
            question=self.question,
            option_text="Red",
            option_count=3
        )
        # Create a vote for one option.
        self.vote = Vote.objects.create(
            option=self.option1,
            voted_by=self.manager
        )

    def test_vote_serializer(self):
        """Test that the VoteSerializer returns the expected data."""
        serializer = VoteSerializer(instance=self.vote)
        data = serializer.data
        self.assertEqual(data['id'], self.vote.id)
        self.assertEqual(data['option'], self.option1.id)
        self.assertEqual(data['voted_by'], self.manager.id)

    def test_option_serializer(self):
        """Test that the OptionSerializer returns the expected data."""
        serializer = OptionSerializer(instance=self.option1)
        data = serializer.data
        self.assertEqual(data['id'], self.option1.id)
        self.assertEqual(data['option_text'], "Blue")
        self.assertEqual(data['option_count'], 5)

    def test_question_serializer(self):
        """Test that the QuestionSerializer returns the expected nested data."""
        serializer = QuestionSerializer(instance=self.question)
        data = serializer.data
        self.assertEqual(data['id'], self.question.id)
        self.assertEqual(data['question_text'], "What is your favorite color?")
        self.assertEqual(len(data['options']), 2)
        option_data_1 = data['options'][0]
        option_data_2 = data['options'][1]
        self.assertEqual(option_data_1['option_text'], "Blue")
        self.assertEqual(option_data_1['option_count'], 5)
        self.assertEqual(option_data_2['option_text'], "Red")
        self.assertEqual(option_data_2['option_count'], 3)
