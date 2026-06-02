import uuid
from django.db import models

def generate_short_id():
    return f"id{uuid.uuid4().hex[:14]}"

class CV(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_short_id, editable=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.id})"

class PersonalDetails(models.Model):
    cv = models.OneToOneField(CV, related_name='personal_details', on_delete=models.CASCADE)
    firstName = models.CharField(max_length=255, blank=True, null=True)
    lastName = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    cityState = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    dateOfBirth = models.CharField(max_length=255, blank=True, null=True)
    placeOfBirth = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True, null=True)
    nationality = models.CharField(max_length=255, blank=True, null=True)
    linkedin = models.CharField(max_length=512, blank=True, null=True)
    github = models.CharField(max_length=512, blank=True, null=True)

    def __str__(self):
        return f"{self.firstName} {self.lastName}"

    class Meta:
        verbose_name_plural = "Personal Details"

class WorkExperience(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_short_id, editable=True)
    cv = models.ForeignKey(CV, related_name='work_experiences', on_delete=models.CASCADE)
    job_title = models.CharField(max_length=255)
    employer = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    city_state = models.CharField(max_length=255, blank=True, null=True)
    description = models.JSONField(blank=True, null=True, default=list)

    def __str__(self):
        return f"{self.job_title} at {self.employer}"

class Education(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_short_id, editable=True)
    cv = models.ForeignKey(CV, related_name='education', on_delete=models.CASCADE)
    school = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    start_date = models.CharField(max_length=100, blank=True, null=True)
    end_date = models.CharField(max_length=100, blank=True, null=True)
    is_current = models.BooleanField(default=False)
    city_state = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.degree} from {self.school}"

class Skill(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_short_id, editable=True)
    cv = models.ForeignKey(CV, related_name='skills', on_delete=models.CASCADE)
    skill_name = models.CharField(max_length=255)
    level = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.skill_name

    class Meta:
        ordering = ['created_at']

class Project(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_short_id, editable=True)
    cv = models.ForeignKey(CV, related_name='projects', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.JSONField(blank=True, null=True, default=list)
    github_link = models.CharField(max_length=512, blank=True, null=True)
    live_link = models.CharField(max_length=512, blank=True, null=True)
    playstore_link = models.CharField(max_length=512, blank=True, null=True)
    applestore_link = models.CharField(max_length=512, blank=True, null=True)
    technologies = models.CharField(max_length=512, blank=True, null=True)

    def __str__(self):
        return self.title

class Language(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_short_id, editable=True)
    cv = models.ForeignKey(CV, related_name='languages', on_delete=models.CASCADE)
    language = models.CharField(max_length=100)
    level = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.language

class Certificate(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_short_id, editable=True)
    cv = models.ForeignKey(CV, related_name='certificates', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    date = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

class Reference(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_short_id, editable=True)
    cv = models.ForeignKey(CV, related_name='references', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.name

class Quality(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_short_id, editable=True)
    cv = models.ForeignKey(CV, related_name='qualities', on_delete=models.CASCADE)
    quality = models.CharField(max_length=255)

    def __str__(self):
        return self.quality

    class Meta:
        verbose_name_plural = "Qualities"

class Summary(models.Model):
    cv = models.OneToOneField(CV, related_name='summary', on_delete=models.CASCADE)
    summary_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Summary for {self.cv.id}"
