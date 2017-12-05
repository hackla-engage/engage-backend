from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from CouncilTag.api import views

urlpatterns = [
    url(r'^agendas/$',views.list_agendas),
    url(r'^tags/$', views.list_tags),
    url(r'^login/$',views.login_user),
]

urlpatterns = format_suffix_patterns(urlpatterns)