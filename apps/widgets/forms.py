from django import forms

class ContactWidgetForm(forms.Form):
    phone = forms.CharField(
        max_length=20,
        required=False,
        label="Phone",
        widget=forms.TextInput(attrs={"placeholder": "Enter phone number"})
    )
    email = forms.EmailField(
        required=False,
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Enter contact email"})
    )
    instagram_username = forms.CharField(
        max_length=50,
        required=False, 
        label="Instagram Username",
        widget=forms.TextInput(attrs={"placeholder": "yourusername (no @)"})
    )
    twitter_username = forms.CharField(
        max_length=50, 
        required=False, 
        label="Twitter Username", 
        widget=forms.TextInput(attrs={"placeholder": "yourusername (no @)"})
    )
    facebook_username = forms.CharField(
        max_length=50, 
        required=False, 
        label="Facebook Username",
        widget=forms.TextInput(attrs={"placeholder": "yourusername"})
    )
    discord_invite = forms.URLField(
        required=False, 
        label="Discord Invite URL",
        widget=forms.URLInput(attrs={"placeholder": "https://discord.com/invite/..." })
    )
    linkedin_username = forms.CharField(
        max_length=50, 
        required=False, 
        label="LinkedIn Username",
        widget=forms.TextInput(attrs={"placeholder": "yourusername"})
    )
    other = forms.CharField(
        required=False,
        label="Additional Information",
        widget=forms.Textarea(attrs={"placeholder": "Any extra details", "rows": 3})
    )