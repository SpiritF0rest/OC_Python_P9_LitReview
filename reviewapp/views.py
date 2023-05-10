import os

from django.shortcuts import render, redirect
from django.db.models import CharField, Value
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.views.generic import View

from authentication.models import User
from . import forms, models
from itertools import chain


@login_required
def home(request):
    tickets = []
    reviews = []
    followed_user = models.UserFollows.objects.filter(user=request.user)
    user_tickets = models.Ticket.objects.filter(user=request.user)
    user_tickets = user_tickets.annotate(content_type=Value('TICKET', CharField()))
    tickets.extend(user_tickets)
    user_reviews = models.Review.objects.filter(user=request.user)
    user_reviews = user_reviews.annotate(content_type=Value('REVIEW', CharField()))
    reviews.extend(user_reviews)
    for ticket in user_tickets:
        user_tickets_reviews = ticket.review_set.all()
        user_tickets_reviews = user_tickets_reviews.annotate(content_type=Value('REVIEW', CharField()))
        reviews.extend(user_tickets_reviews)
    for user in followed_user:
        followed_user_tickets = models.Ticket.objects.filter(user=user.followed_user)
        followed_user_tickets = followed_user_tickets.annotate(content_type=Value('TICKET', CharField()))
        tickets.extend(followed_user_tickets)
        followed_user_reviews = models.Review.objects.filter(user=user.followed_user)
        followed_user_reviews = followed_user_reviews.annotate(content_type=Value('REVIEW', CharField()))
        reviews.extend(followed_user_reviews)
    all_posts = sorted(set(chain(tickets, reviews)), key=lambda instance: instance.time_created, reverse=True)
    return render(request, 'reviewapp/home.html', context={"posts": all_posts})


@login_required
def posts(request):
    tickets = models.Ticket.objects.filter(user=request.user)
    reviews = models.Review.objects.filter(user=request.user)
    all_posts = sorted(chain(tickets, reviews), key=lambda instance: instance.time_created, reverse=True)
    return render(request, 'reviewapp/posts.html', context={"posts": all_posts})


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
            return redirect('posts')
        return render(request, self.template_name, context={"form": form})


# class TicketView(View):
#     template_name = 'reviewapp/ticket.html'
#     form_class = forms.TicketForm
#
#     def get(self, request, ticket_id):
#         ticket = models.Ticket.objects.get(id=ticket_id)
#         return render(request, self.template_name, context={"ticket": ticket})


class ReviewCreationView(View):
    template_name = 'reviewapp/create_review.html'
    form_class = forms.ReviewForm

    def get(self, request, ticket_id):
        ticket = models.Ticket.objects.get(id=ticket_id)
        form = self.form_class()
        return render(request, self.template_name, context={"ticket": ticket, "form": form})

    def post(self, request, ticket_id):
        ticket = models.Ticket.objects.get(id=ticket_id)
        has_review = models.Review.objects.filter(ticket=ticket)
        form = self.form_class(request.POST)
        if form.is_valid() and not has_review:
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


@login_required
def update_ticket(request, ticket_id):
    ticket = models.Ticket.objects.get(id=ticket_id)
    old_image = ticket.image
    if request.method == "POST" and request.user == ticket.user:
        form = forms.TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            if old_image:
                if 'image' not in form.files or ('image' in form.files and form.files["image"] != old_image):
                    os.remove(old_image.path)
            form.save()
            return redirect('posts')
    else:
        form = forms.TicketForm(instance=ticket)
    return render(request, 'reviewapp/update_post.html', {'form': form, "is_ticket": True})


@login_required
def update_review(request, review_id):
    review = models.Review.objects.get(id=review_id)
    if request.method == "POST" and request.user == review.user:
        form = forms.ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('posts')
    else:
        form = forms.ReviewForm(instance=review)
    return render(request, 'reviewapp/update_post.html', {'form': form, "is_ticket": False, 'ticket': review.ticket})


@login_required
def delete_ticket(request, ticket_id):
    ticket = models.Ticket.objects.get(id=ticket_id)
    if request.method == 'POST' and request.user == ticket.user:
        if ticket.image:
            os.remove(ticket.image.path)
        ticket.delete()
        return redirect('posts')
    return render(request, 'reviewapp/delete_post.html', context={"ticket": ticket})


@login_required
def delete_review(request, review_id):
    review = models.Review.objects.get(id=review_id)
    if request.method == 'POST' and request.user == review.user:
        review.delete()
        return redirect('posts')
    return render(request, 'reviewapp/delete_post.html', context={"review": review})


class FollowerAddView(View):
    template_name = 'reviewapp/add_followers.html'

    def follows(self, user):
        subscriptions = models.UserFollows.objects.filter(user=user)
        subscribers = models.UserFollows.objects.filter(followed_user=user)
        return {"subscriptions": subscriptions, "subscribers": subscribers}

    def get(self, request):
        users_links = self.follows(request.user)
        return render(request, self.template_name, context={
            "subscriptions": users_links["subscriptions"],
            "subscribers": users_links["subscribers"]})

    def post(self, request):
        message = ""
        users_links = self.follows(request.user)
        if request.POST.get("username") == request.user.username:
            message = "Vous ne pouvez pas vous abonner à vous-même."
        else:
            try:
                selected_user = User.objects.get(username=request.POST.get("username"))
                subscription = models.UserFollows.objects.filter(user=request.user, followed_user=selected_user)
                if not subscription and selected_user != request.user:
                    new_user_link = models.UserFollows(user=request.user, followed_user=selected_user)
                    new_user_link.save()
                    return redirect("add-follower")
                else:
                    message = f"Vous suivez déjà {selected_user}."
            except ObjectDoesNotExist:
                message = "Merci de saisir un utilisateur correct."
        return render(request, self.template_name, context={
            "message": message,
            "subscriptions": users_links["subscriptions"],
            "subscribers": users_links["subscribers"]})


@login_required
def delete_follower(request, follower_id):
    followed_user = User.objects.get(id=follower_id)
    users_link = models.UserFollows.objects.get(user=request.user, followed_user=followed_user)
    if request.method == 'POST':
        users_link.delete()
        return redirect('add-follower')
    return render(request, 'reviewapp/delete_follower.html', context={"followed_user": followed_user})
