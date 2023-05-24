from django import forms
from reviewapp.models import Ticket, Review


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(widget=forms.RadioSelect, choices=Review.RATING_CHOICES, label=Review.RATING_LABEL)
    body = forms.CharField(widget=forms.Textarea(attrs={"rows": "5"}), label=Review.BODY_LABEL)

    class Meta:
        model = Review
        fields = ['headline', 'rating', 'body']
