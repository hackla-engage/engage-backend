from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from engage.api import views
from .views.Agenda import AgendaView, get_agenda
from .views.AgendaItem import get_agenda_item, get_agenda_item_detail, get_agendaitem_by_tag
from .views.Tags import TagView, UserTagView
from .views.UserFeed import UserFeed
from .views.Auth import SignupView, login_user, update_profile
from .views.Message import addMessage
from .views.Verify import VerifyView
from .views.MailChimp import mailChimpSub

urlpatterns = [
    url(r'^agendas/$', AgendaView.as_view()),
    url(r'^agendas/(?P<meeting_id>[0-9]+)/$', get_agenda),
    url(r'^agendas/item/(?P<agenda_item_id>[0-9]+)/$', get_agenda_item),
    url(r'^agendas/item/(?P<agenda_item_id>[0-9]+)/detail/$', get_agenda_item_detail),
    url(r'^tags/$', TagView.as_view()),
    url(r'^login/$',login_user),
    url(r'^signup/$', SignupView.as_view()),
    url(r'^feed/$', UserFeed.as_view()),
    url(r'^profile/$', update_profile),
    url(r'^tag/(?P<tag_name>[a-zA-Z _]+)/agenda/items/$', get_agendaitem_by_tag),
    url(r'^user/tags/$', UserTagView().as_view()),
    url(r'^add/message/$', addMessage),
    url(r'^verify/$', VerifyView.as_view()),
    url(r'^mailchimp/$', mailChimpSub),

]

urlpatterns = format_suffix_patterns(urlpatterns)