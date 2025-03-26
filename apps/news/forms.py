from django import forms
from apps.news.models import News
from apps.societies.models import Society

class NewsForm(forms.ModelForm):
    """Form for submitting a news post."""

    class Meta:
        model = News
        exclude = [
            'society',
            'is_published',
            'views', 
            'event', 
            'date_posted',
        ]
        # fields = ['title', 'content', 'society', 'date_posted', 'image']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Write news content...'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        """Filter societies based on the logged-in user."""
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # if self.user:
        #     self.fields['society'].queryset = Society.objects.filter(manager=self.user)
