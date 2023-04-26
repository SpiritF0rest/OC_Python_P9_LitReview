from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from . import forms, models


@login_required
def home(request):
    tickets = models.Ticket.objects.all()
    reviews = models.Review.objects.all()
    return render(request, 'reviewapp/home.html', context={"tickets": tickets, "reviews": reviews})


class TicketCreationView(View):
    template_name = 'reviewapp/create_ticket.html'
    form_class = forms.TicketForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, context={"form": form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('ticket', ticket.id)
        return render(request, self.template_name, context={"form": form})


class TicketView(View):
    template_name = 'reviewapp/ticket.html'
    form_class = forms.TicketForm

    def get(self, request, ticket_id):
        ticket = models.Ticket.objects.get(id=ticket_id)
        return render(request, self.template_name, context={"ticket": ticket})


class ReviewCreationView(View):
    template_name = 'reviewapp/create_review.html'
    form_class = forms.ReviewForm

    def get(self, request, ticket_id):
        ticket = models.Ticket.objects.get(id=ticket_id)
        form = self.form_class()
        return render(request, self.template_name, context={"ticket": ticket, "form": form})

    def post(self, request, ticket_id):
        ticket = models.Ticket.objects.get(id=ticket_id)
        form = self.form_class(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.ticket = ticket
            review.user = request.user
            review.save()
            return redirect('home')
        return render(request, self.template_name, context={"ticket": ticket, "form": form})


class FullReviewView(View):
    template_name = 'reviewapp/create_ticket_review.html'
    ticket_form_class = forms.TicketForm
    review_form_class = forms.ReviewForm

    def get(self, request):
        ticket_form = self.ticket_form_class()
        review_form = self.review_form_class()
        return render(request, self.template_name, context={"ticket_form": ticket_form, "review_form": review_form})

    def post(self, request):
        ticket_form = self.ticket_form_class(request.POST, request.FILES)
        review_form = self.review_form_class(request.POST)
        if all([ticket_form.is_valid(), review_form.is_valid()]):
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            review = review_form.save(commit=False)
            review.ticket = ticket
            review.user = request.user
            review.save()
            return redirect('home')
        return render(request, self.template_name, context={"ticket_form": ticket_form, "review_form": review_form})
