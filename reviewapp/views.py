from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from . import forms, models


@login_required
def home(request):
    return render(request, 'reviewapp/home.html', context={})


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
