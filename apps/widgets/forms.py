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
    
    def __init__(self, *args, **kwargs):
        super(ContactWidgetForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
    
class FeaturedMemberForm(forms.Form):
    member = forms.ChoiceField(
        required=True,
        label="Member"
    )
    role = forms.CharField(
        max_length=100,
        required=True,
        label="Role",
        widget=forms.TextInput(attrs={"placeholder": "Enter role (e.g. President)"})
    )
    picture = forms.ImageField(
        required=False,
        label="Picture"
    )

    def __init__(self, *args, **kwargs):
        members_choices = kwargs.pop('members_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['member'].choices = [("", "Select a member")] + [(name, name) for name in members_choices]
        
class AnnouncementForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        required=True,
        label="Announcement Title",
        widget=forms.TextInput(attrs={"placeholder": "Enter announcement title"})
    )
    message = forms.CharField(
        required=True,
        label="Message",
        widget=forms.Textarea(attrs={"placeholder": "Enter announcement message", "rows": 3})
    )
    date = forms.DateField(
        required=False,
        label="Date",
        widget=forms.DateInput(attrs={"type": "date"})
    )
    

class LeaderboardMembershipForm(forms.Form):
    membership_id = forms.IntegerField(widget=forms.HiddenInput)
    member_name = forms.CharField(label="Member", required=False, disabled=True)
    points = forms.IntegerField(label="Points", required=False)
    
    
class LeaderboardSettingsForm(forms.Form):
    display_count = forms.ChoiceField(
        choices=[('3', 'Top 3'), ('5', 'Top 5'), ('10', 'Top 10')],
        required=True,
        label="Number of Top Entries to Display",
        initial='3'
    )
    display_points = forms.BooleanField(
        label="Display Points", 
        required=False
    )
