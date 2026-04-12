from rest_framework import serializers
from .models import (
    CV, PersonalDetails, WorkExperience, Education, Skill, Project, Language,
    Certificate, Reference, Quality, Summary
)

class CVSerializer(serializers.ModelSerializer):
    class Meta:
        model = CV
        fields = '__all__'

class PersonalDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalDetails
        fields = '__all__'

class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = '__all__'

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = '__all__'

class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = '__all__'

class QualitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Quality
        fields = '__all__'

class SummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Summary
        fields = '__all__'
