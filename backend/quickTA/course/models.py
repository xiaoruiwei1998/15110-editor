from django.db import models
import djongo.models as djmodels
from enum import Enum

# Create your models here.
class Course(models.Model):
    _id = models.CharField(max_length=100, editable=False, unique=True)
    
    # Composite Key
    semester = models.CharField(max_length=10)
    course_code = models.CharField(max_length=9)
    course_name = models.TextField(max_length=1000)
    
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    
    students = djmodels.JSONField(default=[], blank=True, null=True)
    instructors = djmodels.JSONField(default=[], blank=True, null=True)
    researchers = djmodels.JSONField(default=[], blank=True, null=True)
    admins = djmodels.JSONField(default=[], blank=True, null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['_id'], name='course_id_idx'),
            models.Index(fields=['course_name'], name='course_name'),
            models.Index(fields=['semester'], name='semester'),
        ]

class CourseDeployment(models.Model):
    _id = models.CharField(max_length=50, editable=False, unique=True)
    name = models.TextField(max_length=1000)
    course_id = models.CharField(max_length=50)
    priority = models.IntegerField(default=0)
    status = models.CharField(default="A", max_length=1) # A or I - Active or Inactive
    conditions = models.IntegerField(default=1)

    # Deployment-wide settings
    assessment_ids = djmodels.JSONField(default=[], blank=True, null=True) # { "assessment_id": assessment_id }
    survey_ids = djmodels.JSONField(default=[], blank=True, null=True) # { "survey_type": Pre/Post, "survey_id": survey_id }

    # Pipeline settings
    pipeline = djmodels.JSONField(default=[], blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['_id'], name='deployment_id_idx'),
            models.Index(fields=['course_id'], name='deployment_course_id_idx'),
        ]


    def to_dict(self, add_details=False):
        deployment = {
            'deployment_id': self.deployment_id,
            'deployment_name': self.deployment_name,
            'course_id': self.course_id,
            'priority': self.priority,
            'status': self.status
        }

        if add_details:
            deployment['assessment_ids'] = self.assessment_ids
            deployment['survey_ids'] = self.survey_ids

        return deployment

class DeploymentStepType(Enum):
    SURVEY = "survey"
    ASSESSMENT = "assessment"
    MODEL = "conversational-agent"
    STATIC = "static"