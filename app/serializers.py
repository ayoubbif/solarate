from rest_framework import serializers
from .models import Project, ProposalUtility

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'id', 'user', 'name', 'description', 'address', 'consumption',
            'percentage', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class ProposalUtilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalUtility
        fields = [
            'id', 'project', 'openei_id', 'rate_name',
            'approved', 'is_default', 'start_date',
            'pricing_matrix', 'average_rate', 'first_year_cost'
        ]