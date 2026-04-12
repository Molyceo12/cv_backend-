from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CVViewSet, PersonalDetailsViewSet, WorkExperienceViewSet, EducationViewSet,
    SkillViewSet, ProjectViewSet, LanguageViewSet,
    CertificateViewSet, ReferenceViewSet, QualityViewSet, SummaryViewSet,
    CVUploadView
)

router = DefaultRouter()
router.register(r'cvs', CVViewSet)
router.register(r'personal-details', PersonalDetailsViewSet)

router.register(r'work-experiences', WorkExperienceViewSet)
router.register(r'education', EducationViewSet)
router.register(r'skill', SkillViewSet)
router.register(r'project', ProjectViewSet)
router.register(r'language', LanguageViewSet)
router.register(r'certificate', CertificateViewSet)
router.register(r'reference', ReferenceViewSet)
router.register(r'quality', QualityViewSet)
router.register(r'summary', SummaryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('upload-cv/', CVUploadView.as_view(), name='upload-cv'),
]
