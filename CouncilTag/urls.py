"""CouncilTag URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import coreapi
import coreschema
from django.contrib import admin
from django.conf.urls import url, include
from rest_framework.documentation import include_docs_urls
from rest_framework import permissions
from openapi_codec import OpenAPICodec
from html_codec import HTMLCodec
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from CouncilTag.ingest.models import Committee, Agenda, AgendaItem
from CouncilTag.api.utils import getLocationBasedDate
from datetime import datetime, timedelta
from CouncilTag.celery import schedule_process_pdf, debug_task

schema_view = get_schema_view(
    openapi.Info(
        title="Engage API Documentation",
        default_version='v1',
        description="Engage API Documentation",
        terms_of_service="https://engage.town/terms/",
        contact=openapi.Contact(email="engage@engage.town"),
        license=openapi.License(name="Apache License v2.0"),
    ),
    # url="https://backend.engage.town/api",
    url="http://localhost:8000/api",

    validators=['flex', 'ssv'],
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('CouncilTag.api.urls')),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(
        cache_timeout=None), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger',
                                           cache_timeout=None), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc',
                                         cache_timeout=None), name='schema-redoc'),
]
