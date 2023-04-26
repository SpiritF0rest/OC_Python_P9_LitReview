from django.contrib import admin
from django.urls import path
import authentication.views
import reviewapp.views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', authentication.views.SignUpView.as_view(), name="signup"),
    path('login/', authentication.views.LoginView.as_view(), name="login"),
    path('logout/', authentication.views.logout_user, name='logout'),
    path('', reviewapp.views.home, name='home'),
    path('tickets/add/', reviewapp.views.TicketCreationView.as_view(), name='ticket-create'),
    path('tickets/<int:ticket_id>/', reviewapp.views.TicketView.as_view(), name='ticket'),
    path('reviews/add/<int:ticket_id>/', reviewapp.views.ReviewCreationView.as_view(), name='review-create'),
    path('tickets/reviews/add', reviewapp.views.FullReviewView.as_view(), name='review-ticket-create')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    