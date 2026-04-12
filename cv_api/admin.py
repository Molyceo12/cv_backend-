from django.contrib import admin
from .models import (
    CV, PersonalDetails, WorkExperience, Education, Skill, 
    Project, Language, Certificate, Reference, Quality
)

class PersonalDetailsInline(admin.StackedInline):
    model = PersonalDetails
    extra = 1

class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    extra = 1

class EducationInline(admin.TabularInline):
    model = Education
    extra = 1

class SkillInline(admin.TabularInline):
    model = Skill
    extra = 3

class ProjectInline(admin.TabularInline):
    model = Project
    extra = 1

class LanguageInline(admin.TabularInline):
    model = Language
    extra = 1

class CertificateInline(admin.TabularInline):
    model = Certificate
    extra = 1

class ReferenceInline(admin.TabularInline):
    model = Reference
    extra = 1

class QualityInline(admin.TabularInline):
    model = Quality
    extra = 3

@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name', 'id')
    inlines = [
        PersonalDetailsInline,
        WorkExperienceInline, 
        EducationInline, 
        SkillInline, 
        ProjectInline, 
        LanguageInline, 
        CertificateInline, 
        ReferenceInline, 
        QualityInline
    ]

# Also register them individually for direct access if needed
admin.site.register(PersonalDetails)
admin.site.register(WorkExperience)
admin.site.register(Education)
admin.site.register(Skill)
admin.site.register(Project)
admin.site.register(Language)
admin.site.register(Certificate)
admin.site.register(Reference)
admin.site.register(Quality)
