from django import forms
from reviewapp.models import Ticket, Review


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(widget=forms.RadioSelect, choices=Review.RATING_CHOICES, label=Review.RATING_LABEL)

    class Meta:
        model = Review
        fields = ['headline', 'rating', 'body']
