from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from CouncilTag.api import views

urlpatterns = [
    url(r'^agendas/$',views.list_agendas),
]

urlpatterns = format_suffix_patterns(urlpatterns)