from django import forms
from .models import Question, Option

class PollForm(forms.Form):
    question_text = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter your question here'}))
    options = forms.CharField(widget=forms.Textarea, required=True, help_text="Enter options, each on a new line")

    def clean_options(self):
        options_data = self.cleaned_data['options']
        options = options_data.splitlines()  # Split the options into a list based on newlines

        # Remove leading/trailing whitespaces from each option
        options = [option.strip() for option in options]

        # Check if there are at least 2 options
        if len(options) < 2:
            raise forms.ValidationError('At least two options are required.')

        return options

    def save(self, user):
        # Get the cleaned data
        question_text = self.cleaned_data['question_text']

        # Create and save the Question object
        question = Question(question_text=question_text)
        question.created_by = user  # Set the current user as the creator
        question.save()

        # Get and save the options
        options = self.cleaned_data['options']
        for option_text in options:
            Option.objects.create(question=question, option_text=option_text.strip())

        return question
