from django.urls import path, re_path
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
from .views.PDF import getPDFLocation

urlpatterns = [
    re_path(r'^agendas/$', AgendaView.as_view()),
    re_path(r'^agendas/(?P<meeting_id>[0-9]+)/$', get_agenda),
    re_path(r'^agendas/item/(?P<agenda_item_id>[0-9]+)/$', get_agenda_item),
    re_path(r'^agendas/item/(?P<agenda_item_id>[0-9]+)/detail/$', get_agenda_item_detail),
    re_path(r'^tags/$', TagView.as_view()),
    re_path(r'^login/$',login_user),
    re_path(r'^signup/$', SignupView.as_view()),
    re_path(r'^feed/$', UserFeed.as_view()),
    re_path(r'^profile/$', update_profile),
    re_path(r'^tag/(?P<tag_name>[a-zA-Z _]+)/agenda/items/$', get_agendaitem_by_tag),
    re_path(r'^user/tags/$', UserTagView().as_view()),
    re_path(r'^add/message/$', addMessage),
    re_path(r'^verify/$', VerifyView.as_view()),
    re_path(r'^mailchimp/$', mailChimpSub),
    re_path(r'^getPDFLocation/(?P<meeting_id>[0-9]+)/$', getPDFLocation),

]

urlpatterns = format_suffix_patterns(urlpatterns)