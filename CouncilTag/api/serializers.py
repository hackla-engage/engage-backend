from rest_framework import serializers
from CouncilTag.ingest.models import Agenda, AgendaItem, Tag, AgendaRecommendation, Committee, Message


class CommitteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Committee
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class AgendaRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgendaRecommendation
        fields = '__all__'


class AgendaItemSerializer(serializers.ModelSerializer):
    recommendations = AgendaRecommendationSerializer(many=True, read_only=True)

    class Meta:
        model = AgendaItem
        exclude = ('tags',)


class AgendaSerializer(serializers.ModelSerializer):
    items = AgendaItemSerializer(many=True, read_only=True, )
    committee = CommitteeSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Agenda
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'


class UserFeedSerializer(serializers.Serializer):
    tag = TagSerializer(read_only=True, many=True)
    item = AgendaItemSerializer(read_only=True)


class VerifySerializer(serializers.Serializer):
    type = serializers.CharField()
    email = serializers.EmailField()
    code = serializers.CharField()
    id = serializers.IntegerField()


class ModifyTagSerializer(serializers.Serializer):
    tags = serializers.ListField(child=serializers.CharField(), min_length=1)


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    zipcode = serializers.IntegerField(default=90401, required=False)
    home_owner = serializers.BooleanField(default=False, required=False)
    resident = serializers.BooleanField(default=False, required=False)
    business_owner = serializers.BooleanField(default=False, required=False)
    works = serializers.BooleanField(default=False, required=False)
    school = serializers.BooleanField(default=False, required=False)
    child_school = serializers.BooleanField(default=False, required=False)

    class Meta:
        extra_kwargs = {'password': {'write_only': True}}


class AddMessageSerializer(serializers.Serializer):
    committee = serializers.CharField(default="Santa Monica City Council")
    ag_item = serializers.CharField(required=True)
    content = serializers.CharField(required=True)
    verify_token = serializers.CharField(required=True)
    pro = serializers.IntegerField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    zipcode = serializers.IntegerField(default=90401)
    home_owner = serializers.BooleanField(default=False, required=False)
    resident = serializers.BooleanField(default=False, required=False)
    business_owner = serializers.BooleanField(default=False, required=False)
    works = serializers.BooleanField(default=False, required=False)
    school = serializers.BooleanField(default=False, required=False)
    child_school = serializers.BooleanField(default=False, required=False)
