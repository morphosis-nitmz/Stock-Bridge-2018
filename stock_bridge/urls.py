from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.views.generic import RedirectView

from .views import home
from accounts.views import RegisterView, LoginView, LeaderBoardView
from market.views import UserTransactionHistoryView


urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^account/', include('accounts.urls', namespace='account')),
    url(r'^accounts/', include('accounts.passwords.urls')),
    url(r'^accounts/$', RedirectView.as_view(url='/account')),
    url(r'^leaderboard/$', LeaderBoardView.as_view(), name='leaderboard'),
    url(r'^stocks/', include('market.urls', namespace='market')),
    url(r'^history/$', UserTransactionHistoryView.as_view(), name='transaction_history'),
    url(r'^bank/', include('bank.urls', namespace='bank')),
    url(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
