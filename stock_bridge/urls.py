from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.views.generic import RedirectView

from .views import HomeView, instruction_view
from accounts.views import RegisterView, LoginView, LeaderBoardView, ProfileView, NewsView


urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^profile/(?P<username>[a-zA-Z0-9_@#\- ]+)/$', ProfileView.as_view(), name='profile'),
    url(r'^news/$', NewsView.as_view(), name='news'),
    url(r'^account/', include('accounts.urls', namespace='account')),
    url(r'^accounts/', include('accounts.passwords.urls')),
    url(r'^accounts/$', RedirectView.as_view(url='/account')),
    url(r'^leaderboard/$', LeaderBoardView.as_view(), name='leaderboard'),
    url(r'^instructions/$', instruction_view, name='instructions'),
    url(r'^stocks/', include('market.urls', namespace='market')),
    url(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
