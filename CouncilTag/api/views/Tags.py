from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from CouncilTag.ingest.models import Agenda, AgendaItem, EngageUserProfile, Tag
from CouncilTag.api.serializers import ModifyTagSerializer, TagSerializer
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework.decorators import api_view
from rest_framework import status, generics


class TagView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    
class UserTagView(LoginRequiredMixin, APIView):
    @swagger_auto_schema(request_body=no_body, responses={"404": "Not logged in, should be 401", "200": "OK, retrieved tags"})
    def get(self, request):
        user = EngageUserProfile.objects.get(user=request.user)
        tags = user.tags.all()
        tags_list = []
        for tag in tags:
            tags_list.append(tag.name)
        return Response(data=tags_list, status=200)

    @swagger_auto_schema(request_body=ModifyTagSerializer, responses={"404": "Not logged in, should be 401", "200": "OK, added tags"})
    def post(self, request):
        '''
        Add new tags (array of tag names) to user's profile
        '''
        if not request.data["tags"]:
            return Response({"error": "tags were not included"}, status=400)
        user = EngageUserProfile.objects.get(user=request.user)
        for tag in request.data["tags"]:
            try:
                tag_to_add = Tag.objects.filter(name__contains=tag).first()
                if tag_to_add is not None:
                    user.tags.add(tag_to_add)
            except:
                username = request.user.username
                print(
                    f"Could not add tag ({tag}) to user ({username}) since it doesn't exist in the ingest_tag table.")
        try:
            user.save()
        except:
            return Response(status=500)
        return Response(status=200)

    @swagger_auto_schema(request_body=ModifyTagSerializer, responses={"404": "Not logged in, should be 401", "200": "OK, removed tags"})
    def delete(self, request):
        '''
        Delete array of existing tags from user
        '''
        if not request.data["tags"]:
            return Response({"error": "tags were not included"}, status=400)
        user = EngageUserProfile.objects.get(user=request.user)
        for tag in request.data["tags"]:
            tag_to_remove = Tag.objects.filter(name__contains=tag).first()
            if tag_to_remove is not None:
                user.tags.remove(tag_to_remove)
        try:
            user.save()
        except:
            return Response(status=500)
        return Response(status=200)
