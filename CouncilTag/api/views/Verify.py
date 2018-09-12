from rest_framework.response import Response
from CouncilTag.ingest.models import Agenda, AgendaItem, EngageUserProfile, Message, Committee
from CouncilTag.api.serializers import AgendaSerializer, AddMessageSerializer, VerifySerializer
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework.decorators import api_view
from rest_framework.views import APIView

from CouncilTag.api.utils import verify_recaptcha, isCommentAllowed, check_auth_code
from django.contrib.auth.models import AnonymousUser
from CouncilTag import settings
from datetime import datetime
from django.contrib.auth import get_user_model
User = get_user_model()


class VerifyView(APIView):
    @swagger_auto_schema(request_body=VerifySerializer)
    def post(self, request):
        """Verify signup for user or email message for non-user"""
        data = request.data
        if 'type' not in data or 'code' not in data or 'email' not in data:
            return Response(data={"error": "Data object must contain code, email, id, and type"}, status=404)
        if data['type'] not in ["email", "signup"]:
            return Response(data={"error": "Data object's type must be signup or email"}, status=404)
        user = User.objects.get(email=data["email"])
        if data['type'] == 'email':
            if 'id' not in data:
                return Response(data={"error": "Data object must contain code, email, id, and type, for email message"}, status=404)
            message = Message.objects.get(id=data['id'])
            if message is None:
                return Response(data={"error": "Message id: " + data['id'] + "was not found"}, status=404)
            authcode = message.authcode
            if authcode is None:
                return Response(data={"error": "Message has already been verified"}, status=200)
            if not check_auth_code(data['code'], authcode):
                return Response(data={"error": "Authcodes do not match for email"}, status=404)
            message.authcode = None
            message.save()
            return Response(status=200, data={"success": True})
        elif data['type'] == 'signup':
            if user is None:
                return Response(data={"error": "User not found"}, status=404)
            profile = EngageUserProfile.objects.get(user=user)
            authcode = profile.authcode
            if authcode is None:
                return Response(data={"error": "User has already been verified"}, status=200)
            if not check_auth_code(data['code'], authcode):
                return Response(data={"error": "Authcodes do not match for email"}, status=404)
            profile.authcode = None
            profile.save()
            return Response(status=200, data={"success": True})
        return Response(status=500)
