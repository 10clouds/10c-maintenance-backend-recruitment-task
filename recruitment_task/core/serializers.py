from rest_framework import serializers

from core.models import Project, Investor


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"
        read_only_field = ["funded", "funded_by"]


class InvestorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investor
        fields = "__all__"
        read_only_fields = ["remaining_amount"]


class ProjectDetailsSerializer(serializers.ModelSerializer):
    possible_investors = serializers.ReadOnlyField()

    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = ["funded", "funded_by"]


class InvestorDetailsSerializer(serializers.ModelSerializer):
    possible_projects = serializers.ReadOnlyField()

    class Meta:
        model = Investor
        fields = "__all__"
        read_only_fields = ["remaining_amount"]
