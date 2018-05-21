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
    items = AgendaItemSerializer(many=True, read_only=True)
    committee = CommitteeSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True )
    class Meta:
        model = Agenda
        fields ='__all__'

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

class UserFeedSerializer(serializers.Serializer):
    tag = TagSerializer(read_only=True, many=True)
    item  = AgendaItemSerializer(read_only=True)



