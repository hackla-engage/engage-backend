from rest_framework import serializers
from CouncilTag.injest.models import Agenda, AgendaItem, AgendaRecommendation, Committee

class CommitteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Committee
        fields = '__all__'

class AgendaRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgendaRecommendation
        fields = '__all__'


class AgendaItemSerializer(serializers.ModelSerializer):
    recommendations = AgendaRecommendationSerializer(many=True, read_only=True)
    class Meta:
        model = AgendaItem
        fields = '__all__'

class AgendaSerializer(serializers.ModelSerializer):
    items = AgendaItemSerializer(many=True, read_only=True)
    committee = CommitteeSerializer(read_only=True)
    class Meta:
        model = Agenda
        fields ='__all__'
