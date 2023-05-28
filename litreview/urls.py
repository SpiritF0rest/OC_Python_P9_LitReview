from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

import authentication.views
import reviewapp.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', authentication.views.SignUpView.as_view(), name="signup"),
    path('login/', authentication.views.LoginView.as_view(), name="login"),
    path('logout/', authentication.views.logout_user, name='logout'),
    path('', reviewapp.views.Home.as_view(), name='home'),
    path('posts/', reviewapp.views.Posts.as_view(), name='posts'),
    path('tickets/add/', reviewapp.views.TicketCreationView.as_view(), name='ticket-create'),
    path('tickets/<int:ticket_id>/update/', reviewapp.views.UpdateTicketView.as_view(), name='update-ticket'),
    path('tickets/<int:ticket_id>/delete/', reviewapp.views.DeleteTicketView.as_view(), name='delete-ticket'),
    path('tickets/<int:ticket_id>/review/add/', reviewapp.views.ReviewCreationView.as_view(), name='review-create'),
    path('review/<int:review_id>/update/', reviewapp.views.UpdateReviewView.as_view(), name='update-review'),
    path('review/<int:review_id>/delete/', reviewapp.views.DeleteReviewView.as_view(), name='delete-review'),
    path('tickets/review/add/', reviewapp.views.FullReviewView.as_view(), name='review-ticket-create'),
    path('follower/add/', reviewapp.views.FollowerAddView.as_view(), name='add-follower'),
    path('follower/<int:follower_id>/delete/', reviewapp.views.DeleteFollowerView.as_view(), name='delete-follower')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
