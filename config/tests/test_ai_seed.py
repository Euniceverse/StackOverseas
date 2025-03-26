from types import ModuleType
import sys

dummy_constants = ModuleType("constants")
dummy_constants.EVENT_TYPE_CHOICES = [("sports", "Sports"), ("academic", "Academic")]
sys.modules["constants"] = dummy_constants

import unittest
from unittest.mock import patch, MagicMock
import random
import string
import requests
from django.test import SimpleTestCase
import config.ai_seed as ai_seed

class GenerateSocietyNameTest(SimpleTestCase):
    @patch('config.ai_seed.random.choice')
    def test_generate_society_name_known_type(self, mock_random_choice):
        mock_random_choice.side_effect = lambda seq: seq[0]
        existing_names = set()
        name = ai_seed.generate_society_name("sports", existing_names)
        expected = f"{ai_seed.ADJECTIVES[0]} {ai_seed.NOUNS['sports'][0]}"
        self.assertEqual(name, expected)
        self.assertIn(name, existing_names)

    def test_generate_society_name_unknown_type(self):
        existing_names = set()
        name = ai_seed.generate_society_name("nonexistent", existing_names)
        self.assertTrue(len(name) > 0)
        self.assertIn(name, existing_names)

class GenerateSocietyDescriptionTest(SimpleTestCase):
    def test_generate_society_description(self):
        society_name = "Elite Society"
        society_type = "arts"
        description = ai_seed.generate_society_description(society_name, society_type)
        expected = (
            f"{society_name} is a vibrant society dedicated to {society_type} activities. "
            "Join us to learn, grow, and connect with others who share the same passion!"
        )
        self.assertEqual(description, expected)

class GenerateEventLocationTest(SimpleTestCase):
    def test_generate_event_location_online(self):
        location = ai_seed.generate_event_location("Online")
        self.assertEqual(location, "Online")

    @patch('config.ai_seed.requests.get')
    def test_generate_event_location_success(self, mock_requests_get):
        fake_data = [{"display_name": "Fake Address, UK"}]
        mock_response = MagicMock()
        mock_response.json.return_value = fake_data
        mock_requests_get.return_value = mock_response

        location = ai_seed.generate_event_location("London")
        self.assertEqual(location, "Fake Address, UK")

    @patch('config.ai_seed.requests.get')
    def test_generate_event_location_empty_response(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_requests_get.return_value = mock_response

        location = ai_seed.generate_event_location("London")
        self.assertEqual(location, "London, UK")

    @patch('config.ai_seed.requests.get', side_effect=requests.RequestException("API Error"))
    def test_generate_event_location_exception(self, mock_requests_get):
        location = ai_seed.generate_event_location("London")
        self.assertEqual(location, "London, UK")


if __name__ == '__main__':
    unittest.main()