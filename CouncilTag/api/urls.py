from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from CouncilTag.api import views
urlpatterns = [
    url(r'^agendas/$',views.AgendaView.as_view()),
    url(r'^agendas/(?P<meeting_id>[0-9]+)/$', views.get_agenda),
    url(r'^agendas/item/(?P<agenda_item_id>[0-9]+)/$', views.get_agenda_item),
    url(r'^agendas/item/(?P<agenda_item_id>[0-9]+)/detail/$', views.get_agenda_item_detail),
    url(r'^tags/$', views.TagView.as_view()),
    url(r'^login/$',views.login_user),
    url(r'^signup/$', views.SignupView.as_view()),
    url(r'^feed/$', views.UserFeed.as_view()),
    url(r'^profile/$', views.update_profile),
    url(r'^tag/(?P<tag_name>[a-zA-Z _]+)/agenda/items/$', views.get_agendaitem_by_tag),
    url(r'^user/tags/$', views.UserTagView().as_view()),
    url(r'^add/message/$', views.AddMessageView.as_view()),
    url(r'^verify/$', views.VerifyView.as_view())

]

urlpatterns = format_suffix_patterns(urlpatterns)