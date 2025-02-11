from django import forms
from apps.news.models import News
from apps.societies.models import Society

class NewsForm(forms.ModelForm):
    """Form for submitting a news post."""

    society = forms.ModelChoiceField(
        queryset=Society.objects.none(), 
        required=True,
        label="Select Society",
        help_text="Choose the society you want to submit news for."
    )

    class Meta:
        model = News
        fields = ['title', 'content', 'society', 'date_posted', 'image']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Write news content...'}),
            'date_posted': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        """Filter societies based on the logged-in user."""
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields['society'].queryset = Society.objects.filter(manager=self.user)
