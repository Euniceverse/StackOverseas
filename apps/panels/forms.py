from django import forms
from django.forms import modelformset_factory
from .models import Comment, Poll, Gallery, Image, Question, Option

#comments
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        # widgets = {
        #     'content': forms.Textarea(attrs={ 'class': 'form-control', 'rows': 3, 'placeholder': 'Make a comment...'}),
        # }
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

#gallery
class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ['title', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']

#poll
class PollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ['title', 'description', 'deadline']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text']

OptionFormSet = modelformset_factory(
    Option,
    fields=('option_text',),
    extra=0, 
    can_delete=False
)
