from django import forms
from members.models import Member


class EmailBlastForm(forms.Form):
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'placeholder': 'Email subject...'}))
    body = forms.CharField(widget=forms.Textarea(attrs={'rows': 8, 'placeholder': 'Compose your message...'}))
    recipients = forms.ModelMultipleChoiceField(
        queryset=Member.objects.filter(status='active'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text='Leave empty to send to all active members.',
    )
