from django.conf.urls import url
from CouncilTag.frontend.views import home_page
urlpatterns += [
    url(r'^$', home_page, name="home_page" ),
]