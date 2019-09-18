"""engage URL Configuration

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
import os
from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import include
from rest_framework.documentation import include_docs_urls
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from engage.ingest.models import Committee, Agenda, AgendaItem
from datetime import datetime, timedelta
from engage import settings
if settings.TEST:
    url = "http://localhost:8000/api"
else:
    url="https://backend.engage.town/api"

schema_view = get_schema_view(
    openapi.Info(
        title="Engage API Documentation",
        default_version='v1',
        description="Engage API Documentation",
        terms_of_service="https://engage.town/terms/",
        contact=openapi.Contact(email="engage@engage.town"),
        license=openapi.License(name="Apache License v2.0"),
    ),
    url=url,
    validators=['flex', 'ssv'],
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    re_path(r'api/', include('engage.api.urls')),
    re_path(r'swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(
        cache_timeout=None), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger',
                                           cache_timeout=None), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc',
                                         cache_timeout=None), name='schema-redoc'),
]
