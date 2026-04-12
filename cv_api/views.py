from rest_framework import viewsets
from rest_framework.decorators import action
from .models import (
    CV, PersonalDetails, WorkExperience, Education, Skill, Project, Language,
    Certificate, Reference, Quality, Summary, generate_short_id
)
from .serializers import (
    CVSerializer, PersonalDetailsSerializer, WorkExperienceSerializer, EducationSerializer,
    SkillSerializer, ProjectSerializer, LanguageSerializer,
    CertificateSerializer, ReferenceSerializer, QualitySerializer, SummarySerializer
)

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .utils import extract_text_from_pdf, parse_cv_with_gemini

class CVViewSet(viewsets.ModelViewSet):
    queryset = CV.objects.all()
    serializer_class = CVSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            "message": "CV created successfully",
            "body": serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "message": "CV updated successfully",
            "body": serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "message": "CV deleted successfully"
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        old_cv = self.get_object()
        new_cv = CV.objects.create(name=f"{old_cv.name} (Copy)")

        if hasattr(old_cv, 'personal_details'):
            pd = old_cv.personal_details
            pd.pk = None
            pd.cv = new_cv
            pd.save()

        if hasattr(old_cv, 'summary'):
            summary = old_cv.summary
            summary.pk = None
            summary.cv = new_cv
            summary.save()

        relations = [
            'work_experiences', 'education', 'skills', 'projects',
            'languages', 'certificates', 'references', 'qualities'
        ]

        for rel in relations:
            for item in getattr(old_cv, rel).all():
                item.pk = None
                # generate new primary key since we are duplicating
                item.id = generate_short_id()
                item.cv = new_cv
                item.save()

        serializer = self.get_serializer(new_cv)
        return Response({
            "message": "CV duplicated successfully",
            "body": serializer.data
        }, status=status.HTTP_201_CREATED)

class BaseCVChildViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        queryset = super().get_queryset()
        cv_id = self.request.query_params.get('cv', None)
        if cv_id is not None:
            queryset = queryset.filter(cv_id=cv_id)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            "message": "Record created successfully",
            "body": serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "message": "Record updated successfully",
            "body": serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "message": "Record deleted successfully"
        }, status=status.HTTP_200_OK)


class PersonalDetailsViewSet(BaseCVChildViewSet):
    queryset = PersonalDetails.objects.all()
    serializer_class = PersonalDetailsSerializer
    lookup_field = 'cv'

    def create(self, request, *args, **kwargs):
        # Handle "Upsert" logic: If details for this CV already exist, update them instead of failing.
        cv_id = request.data.get('cv')
        if cv_id:
            instance = PersonalDetails.objects.filter(cv_id=cv_id).first()
            if instance:
                # Manually update fields from request.data to ensure nulls/blanks are saved correctly
                fields = [
                    'firstName', 'lastName', 'email', 'phone', 'address',
                    'cityState', 'country', 'dateOfBirth', 'placeOfBirth',
                    'gender', 'nationality', 'linkedin', 'github'
                ]
                for field in fields:
                    if field in request.data:
                        setattr(instance, field, request.data.get(field))
                
                instance.save()
                serializer = self.get_serializer(instance)
                return Response({
                    "message": "Personal details updated successfully",
                    "body": serializer.data
                }, status=status.HTTP_200_OK)
        
        return super().create(request, *args, **kwargs)

class WorkExperienceViewSet(BaseCVChildViewSet):
    queryset = WorkExperience.objects.all()
    serializer_class = WorkExperienceSerializer

class WorkExperienceViewSet(BaseCVChildViewSet):
    queryset = WorkExperience.objects.all()
    serializer_class = WorkExperienceSerializer

    def partial_update(self, request, *args, **kwargs):
        """Standard PATCH /api/work-experiences/{id}/ for updates."""
        instance = self.get_object()
        return self._manual_update(instance, request.data)

    def _manual_update(self, instance, data):
        # Manually update fields (direct mapping for null support)
        fields = [
            'job_title', 'employer', 'start_date', 'end_date', 
            'is_current', 'city_state', 'description'
        ]
        for field in fields:
            if field in data:
                setattr(instance, field, data.get(field))
        
        instance.save()
        serializer = self.get_serializer(instance)
        return Response({
            "message": "Work experience updated successfully",
            "body": serializer.data
        }, status=status.HTTP_200_OK)

class EducationViewSet(BaseCVChildViewSet):
    queryset = Education.objects.all()
    serializer_class = EducationSerializer

    def partial_update(self, request, *args, **kwargs):
        """Standard PATCH /api/education/{id}/ for updates."""
        instance = self.get_object()
        return self._manual_update(instance, request.data)

    def _manual_update(self, instance, data):
        # Manually update fields (direct mapping for null support)
        fields = [
            'school', 'degree', 'start_date', 'end_date', 
            'is_current', 'city_state', 'description'
        ]
        for field in fields:
            if field in data:
                setattr(instance, field, data.get(field))
        
        instance.save()
        serializer = self.get_serializer(instance)
        return Response({
            "message": "Education updated successfully",
            "body": serializer.data
        }, status=status.HTTP_200_OK)

class SkillViewSet(BaseCVChildViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

    def create(self, request, *args, **kwargs):
        """Supports single object and bulk upsert. Matches by ID or (CV + Skill Name)."""
        data = request.data
        if isinstance(data, list):
            results = []
            for item in data:
                pk = item.get('id')
                name = item.get('skill_name')
                cv_id = item.get('cv')
                
                instance = None
                if pk:
                    instance = Skill.objects.filter(id=pk).first()
                elif name and cv_id:
                    instance = Skill.objects.filter(cv_id=cv_id, skill_name=name).first()

                if instance:
                    # Update existing
                    self._manual_update_fields(instance, item)
                    results.append(self.get_serializer(instance).data)
                    continue
                
                # Create new if no ID or ID not found
                serializer = self.get_serializer(data=item)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                results.append(serializer.data)
                
            return Response({
                "message": "Skills processed successfully",
                "body": results
            }, status=status.HTTP_201_CREATED)
        
        return super().create(request, *args, **kwargs)

    def _manual_update_fields(self, instance, data):
        # Manually update fields (direct mapping for null support)
        fields = ['skill_name', 'level']
        for field in fields:
            if field in data:
                setattr(instance, field, data.get(field))
        instance.save()

class ProjectViewSet(BaseCVChildViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def create(self, request, *args, **kwargs):
        """Supports single object and bulk creation (no update/match)."""
        data = request.data
        if isinstance(data, list):
            results = []
            for item in data:
                serializer = self.get_serializer(data=item)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                results.append(serializer.data)
                
            return Response({
                "message": "Projects created successfully",
                "body": results
            }, status=status.HTTP_201_CREATED)
        
        return super().create(request, *args, **kwargs)

class LanguageViewSet(BaseCVChildViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer

    def create(self, request, *args, **kwargs):
        """Supports single object and bulk upsert. Matches by ID or (CV + Language)."""
        data = request.data
        if isinstance(data, list):
            results = []
            for item in data:
                pk = item.get('id')
                name = item.get('language')
                cv_id = item.get('cv')

                instance = None
                if pk:
                    instance = Language.objects.filter(id=pk).first()
                elif name and cv_id:
                    instance = Language.objects.filter(cv_id=cv_id, language=name).first()

                if instance:
                    self._manual_update_fields(instance, item)
                    results.append(self.get_serializer(instance).data)
                    continue
                
                serializer = self.get_serializer(data=item)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                results.append(serializer.data)
                
            return Response({
                "message": "Languages processed successfully",
                "body": results
            }, status=status.HTTP_201_CREATED)
        
        return super().create(request, *args, **kwargs)

    def _manual_update_fields(self, instance, data):
        fields = ['language', 'level']
        for field in fields:
            if field in data:
                setattr(instance, field, data.get(field))
        instance.save()

class CertificateViewSet(BaseCVChildViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer

    def partial_update(self, request, *args, **kwargs):
        """Standard PATCH /api/certificate/{id}/ for updates."""
        instance = self.get_object()
        fields = ['title', 'date', 'description']
        for field in fields:
            if field in request.data:
                setattr(instance, field, request.data.get(field))
        
        instance.save()
        serializer = self.get_serializer(instance)
        return Response({
            "message": "Certificate updated successfully",
            "body": serializer.data
        }, status=status.HTTP_200_OK)

class ReferenceViewSet(BaseCVChildViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer

    def partial_update(self, request, *args, **kwargs):
        """Standard PATCH /api/references/{id}/ for updates."""
        instance = self.get_object()
        fields = ['name', 'role', 'company', 'phone', 'email']
        for field in fields:
            if field in request.data:
                setattr(instance, field, request.data.get(field))
        
        instance.save()
        serializer = self.get_serializer(instance)
        return Response({
            "message": "Reference updated successfully",
            "body": serializer.data
        }, status=status.HTTP_200_OK)

class QualityViewSet(BaseCVChildViewSet):
    queryset = Quality.objects.all()
    serializer_class = QualitySerializer

    def create(self, request, *args, **kwargs):
        """Supports single object and bulk upsert. Matches by ID or (CV + Quality)."""
        data = request.data
        if isinstance(data, list):
            results = []
            for item in data:
                pk = item.get('id')
                name = item.get('quality')
                cv_id = item.get('cv')

                instance = None
                if pk:
                    instance = Quality.objects.filter(id=pk).first()
                elif name and cv_id:
                    instance = Quality.objects.filter(cv_id=cv_id, quality=name).first()

                if instance:
                    self._manual_update_fields(instance, item)
                    results.append(self.get_serializer(instance).data)
                    continue
                
                serializer = self.get_serializer(data=item)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                results.append(serializer.data)
                
            return Response({
                "message": "Qualities processed successfully",
                "body": results
            }, status=status.HTTP_201_CREATED)
        
        return super().create(request, *args, **kwargs)

    def _manual_update_fields(self, instance, data):
        fields = ['quality']
        for field in fields:
            if field in data:
                setattr(instance, field, data.get(field))
        instance.save()

class SummaryViewSet(BaseCVChildViewSet):
    queryset = Summary.objects.all()
    serializer_class = SummarySerializer
    lookup_field = 'cv'

    def create(self, request, *args, **kwargs):
        # Handle Upsert logic for Summary (OneToOne)
        cv_id = request.data.get('cv')
        if cv_id:
            instance = Summary.objects.filter(cv_id=cv_id).first()
            if instance:
                instance.summary_text = request.data.get('summary_text', instance.summary_text)
                instance.save()
                serializer = self.get_serializer(instance)
                return Response({
                    "message": "Summary updated successfully",
                    "body": serializer.data
                }, status=status.HTTP_200_OK)
        
        return super().create(request, *args, **kwargs)


class CVUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        if not file.name.lower().endswith('.pdf'):
            return Response({"error": "Only PDF files are supported"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Extract raw text from PDF
        text = extract_text_from_pdf(file)
        if not text:
            return Response({"error": "Could not extract text from PDF"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        # 2. Parse with Gemini
        try:
            parsed = parse_cv_with_gemini(text)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": f"Gemini parsing failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 3. Save everything to the database
        personal = parsed.get("personal_details", {})
        first = personal.get("firstName") or "Uploaded"
        last = personal.get("lastName") or "CV"
        cv = CV.objects.create(name=f"{first} {last}".strip())

        # Personal Details
        PersonalDetails.objects.create(
            cv=cv,
            firstName=personal.get("firstName"),
            lastName=personal.get("lastName"),
            email=personal.get("email"),
            phone=personal.get("phone"),
            address=personal.get("address"),
            cityState=personal.get("cityState"),
            country=personal.get("country"),
            dateOfBirth=personal.get("dateOfBirth"),
            placeOfBirth=personal.get("placeOfBirth"),
            gender=personal.get("gender"),
            nationality=personal.get("nationality"),
            linkedin=personal.get("linkedin"),
            github=personal.get("github"),
        )

        # Summary
        if parsed.get("summary"):
            Summary.objects.create(cv=cv, summary_text=parsed["summary"])

        # Work Experiences
        for item in parsed.get("work_experiences", []):
            try:
                WorkExperience.objects.create(
                    cv=cv,
                    job_title=item.get("job_title", ""),
                    employer=item.get("employer", ""),
                    start_date=item.get("start_date") or "2000-01-01",
                    end_date=item.get("end_date"),
                    is_current=item.get("is_current", False),
                    city_state=item.get("city_state"),
                    description=item.get("description", []),
                )
            except Exception:
                pass  # Skip malformed entries

        # Education
        for item in parsed.get("education", []):
            Education.objects.create(
                cv=cv,
                school=item.get("school", ""),
                degree=item.get("degree", ""),
                start_date=item.get("start_date"),
                end_date=item.get("end_date"),
                is_current=item.get("is_current", False),
                city_state=item.get("city_state"),
                description=item.get("description"),
            )

        # Skills
        for item in parsed.get("skills", []):
            if item.get("skill_name"):
                Skill.objects.create(cv=cv, skill_name=item["skill_name"], level=item.get("level"))

        # Languages
        for item in parsed.get("languages", []):
            if item.get("language"):
                Language.objects.create(cv=cv, language=item["language"], level=item.get("level"))

        # Certificates
        for item in parsed.get("certificates", []):
            if item.get("title"):
                Certificate.objects.create(
                    cv=cv,
                    title=item["title"],
                    date=item.get("date"),
                    description=item.get("description"),
                )

        # Projects
        for item in parsed.get("projects", []):
            if item.get("title"):
                Project.objects.create(
                    cv=cv,
                    title=item["title"],
                    description=item.get("description", []),
                    github_link=item.get("github_link"),
                    live_link=item.get("live_link"),
                    technologies=item.get("technologies"),
                )

        # Qualities
        for item in parsed.get("qualities", []):
            if item.get("quality"):
                Quality.objects.create(cv=cv, quality=item["quality"])

        # References
        for item in parsed.get("references", []):
            if item.get("name"):
                Reference.objects.create(
                    cv=cv,
                    name=item["name"],
                    role=item.get("role"),
                    company=item.get("company"),
                    phone=item.get("phone"),
                    email=item.get("email") or None,
                )

        # 4. Return full CV data
        serializer = CVSerializer(cv)
        return Response({
            "message": "CV created successfully",
            "body": serializer.data
        }, status=status.HTTP_201_CREATED)


