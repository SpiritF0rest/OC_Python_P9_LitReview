import os
from itertools import chain

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import CharField, Value
from django.shortcuts import render, redirect
from django.views.generic import View

from authentication.models import User
from . import forms, models


def get_user_tickets(user):
    tickets = models.Ticket.objects.filter(user=user)
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))
    return tickets


def get_user_reviews(user):
    reviews = models.Review.objects.filter(user=user)
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))
    return reviews


def get_ticket_by_id(ticket_id):
    ticket = models.Ticket.objects.get(id=ticket_id)
    return ticket


def get_review_by_id(review_id):
    review = models.Review.objects.get(id=review_id)
    return review


class Home(LoginRequiredMixin, View):
    template_name = 'reviewapp/home.html'

    def get(self, request):
        tickets = []
        reviews = []
        followed_user = models.UserFollows.objects.filter(user=request.user)
        user_tickets = get_user_tickets(request.user)
        tickets.extend(user_tickets)
        user_reviews = get_user_reviews(request.user)
        reviews.extend(user_reviews)
        for ticket in user_tickets:
            user_tickets_reviews = ticket.review_set.all()
            user_tickets_reviews = user_tickets_reviews.annotate(content_type=Value('REVIEW', CharField()))
            reviews.extend(user_tickets_reviews)
        for user in followed_user:
            followed_user_tickets = get_user_tickets(user.followed_user)
            tickets.extend(followed_user_tickets)
            followed_user_reviews = get_user_reviews(user.followed_user)
            reviews.extend(followed_user_reviews)
        all_posts = sorted(set(chain(tickets, reviews)), key=lambda instance: instance.time_created, reverse=True)
        return render(request, self.template_name, context={"posts": all_posts})


class Posts(LoginRequiredMixin, View):
    template_name = 'reviewapp/posts.html'

    def get(self, request):
        tickets = get_user_tickets(request.user)
        reviews = get_user_reviews(request.user)
        all_posts = sorted(chain(tickets, reviews), key=lambda instance: instance.time_created, reverse=True)
        return render(request, self.template_name, context={"posts": all_posts})


class TicketCreationView(LoginRequiredMixin, View):
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


class ReviewCreationView(LoginRequiredMixin, View):
    template_name = 'reviewapp/create_review.html'
    form_class = forms.ReviewForm

    def get(self, request, ticket_id):
        ticket = get_ticket_by_id(ticket_id)
        form = self.form_class()
        return render(request, self.template_name, context={"ticket": ticket, "form": form})

    def post(self, request, ticket_id):
        ticket = get_ticket_by_id(ticket_id)
        has_review = models.Review.objects.filter(ticket=ticket).exists()
        form = self.form_class(request.POST)
        if form.is_valid() and not has_review:
            review = form.save(commit=False)
            review.ticket = ticket
            review.user = request.user
            review.save()
            return redirect('home')
        return render(request, self.template_name, context={"ticket": ticket, "form": form})


class FullReviewView(LoginRequiredMixin, View):
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


class UpdateTicketView(LoginRequiredMixin, View):
    template_name = 'reviewapp/update_post.html'
    ticket_form_class = forms.TicketForm
    update_image_form_class = forms.UpdateTicketWithImageForm

    def get(self, request, ticket_id):
        ticket = get_ticket_by_id(ticket_id)
        if ticket.image:
            form = self.update_image_form_class(instance=ticket)
        else:
            form = self.ticket_form_class(instance=ticket)
        return render(request, self.template_name, context={'form': form, "is_ticket": True})

    def post(self, request, ticket_id):
        ticket = get_ticket_by_id(ticket_id)
        old_image = ticket.image
        if request.user == ticket.user:
            if ticket.image:
                form = self.update_image_form_class(request.POST, request.FILES, instance=ticket)
            else:
                form = self.ticket_form_class(request.POST, request.FILES, instance=ticket)
            if form.is_valid():
                updated_ticket = form.save(commit=False)
                if old_image:
                    if "image-clear" in request.POST:
                        os.remove(old_image.path)
                        updated_ticket.image = ""
                    elif 'image' in form.files and form.files["image"] != old_image:
                        os.remove(old_image.path)
                updated_ticket.save()
                return redirect('posts')
            return render(request, self.template_name, context={'form': form, "is_ticket": True})
        return redirect('posts')


class UpdateReviewView(LoginRequiredMixin, View):
    template_name = 'reviewapp/update_post.html'
    review_form_class = forms.ReviewForm

    def get(self, request, review_id):
        review = get_review_by_id(review_id)
        form = self.review_form_class(instance=review)
        return render(request, self.template_name, context={'form': form, "is_ticket": False, 'ticket': review.ticket})

    def post(self, request, review_id):
        review = get_review_by_id(review_id)
        if request.user == review.user:
            form = self.review_form_class(request.POST, instance=review)
            if form.is_valid():
                form.save()
                return redirect('posts')
            return render(request, self.template_name, context={
                'form': form,
                "is_ticket": False,
                'ticket': review.ticket})
        return redirect('posts')


class DeleteTicketView(LoginRequiredMixin, View):
    template_name = 'reviewapp/delete_post.html'

    def get(self, request, ticket_id):
        ticket = get_ticket_by_id(ticket_id)
        return render(request, self.template_name, context={"ticket": ticket})

    def post(self, request, ticket_id):
        ticket = get_ticket_by_id(ticket_id)
        if request.user == ticket.user:
            if ticket.image:
                os.remove(ticket.image.path)
            ticket.delete()
            return redirect('posts')
        message = "Vous n'avez pas les droits pour supprimer ce ticket."
        return render(request, self.template_name, context={"ticket": ticket, "message": message})


class DeleteReviewView(LoginRequiredMixin, View):
    template_name = 'reviewapp/delete_post.html'

    def get(self, request, review_id):
        review = get_review_by_id(review_id)
        return render(request, self.template_name, context={"review": review})

    def post(self, request, review_id):
        review = get_review_by_id(review_id)
        if request.user == review.user:
            review.delete()
            return redirect('posts')
        message = "Vous n'avez pas les droits pour supprimer cette critique."
        return render(request, self.template_name, context={"review": review, "message": message})


class FollowerAddView(LoginRequiredMixin, View):
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
        users_links = self.follows(request.user)
        if request.POST.get("username") == request.user.username:
            message = "Vous ne pouvez pas vous abonner à vous-même."
        else:
            try:
                selected_user = User.objects.get(username=request.POST.get("username"))
                subscription = models.UserFollows.objects\
                    .filter(user=request.user, followed_user=selected_user)\
                    .exists()
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


class DeleteFollowerView(LoginRequiredMixin, View):
    template_name = 'reviewapp/delete_follower.html'

    def get(self, request, follower_id):
        followed_user = User.objects.get(id=follower_id)
        return render(request, self.template_name, context={"followed_user": followed_user})

    def post(self, request, follower_id):
        followed_user = User.objects.get(id=follower_id)
        users_link = models.UserFollows.objects.filter(user=request.user, followed_user=followed_user).exists()
        if users_link:
            models.UserFollows.objects.get(user=request.user, followed_user=followed_user).delete()
            return redirect('add-follower')
        message = "Vous n'êtes pas abonné à cet utilisateur."
        return render(request, self.template_name, context={"followed_user": followed_user, "message": message})
