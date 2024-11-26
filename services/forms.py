from django import forms
from django.core.exceptions import ValidationError

class SearchForm(forms.Form):
    query = forms.CharField(label="Search", max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Search...'}))


class URLSearchForm(forms.Form):
    url = forms.URLField(label='URL kiriting', widget=forms.URLInput(attrs={'placeholder': 'https://example.com'}))

    def clean_url(self):
        url = self.cleaned_data.get('url')

        # Check if URL is empty or None
        if not url:
            raise ValidationError('URL maydoni bo\'sh bo\'lishi mumkin emas.')

        # Strip any leading/trailing whitespaces
        url = url.strip()

        # Check if URL starts with 'http://' or 'https://'
        if not (url.startswith('http://') or url.startswith('https://')):
            raise ValidationError('URL faqat http:// yoki https:// bilan boshlanishi kerak.')

        # Optionally, you can add more validations (e.g., URL length or specific domain check)

        return url
    





class BalanceForm(forms.Form):
    amount = forms.FloatField(required=True)
    picture = forms.ImageField(required=True)
