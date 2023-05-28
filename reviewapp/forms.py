from string import Template

from django import forms
from django.utils.safestring import mark_safe

from litreview import settings
from reviewapp.models import Ticket, Review


class PictureWidget(forms.widgets.FileInput):
    def render(self, name, value, attrs=None, renderer=None):
        html = Template("""
        <div class="image">
            <img src="$media$link"/>
        </div>
        <div>
            <label for="image-clear_id">Effacer</label>
            <input type="checkbox" name="image-clear" id="image-clear_id">
        </div>
        <p>Modification:</p>
        <input type="file" name="image" accept="image/*" id="id_image">
        """)
        return mark_safe(html.substitute(media=settings.MEDIA_URL, link=value))


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']


class UpdateTicketWithImageForm(forms.ModelForm):
    image = forms.ImageField(widget=PictureWidget)

    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(widget=forms.RadioSelect, choices=Review.RATING_CHOICES, label=Review.RATING_LABEL)
    body = forms.CharField(widget=forms.Textarea(attrs={"rows": "5"}), label=Review.BODY_LABEL, required=False)

    class Meta:
        model = Review
        fields = ['headline', 'rating', 'body']
