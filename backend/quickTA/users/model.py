from django.db import models
import djongo.models as djmodels
from django.db.models import Model

# Create your models here.
class User(Model):

    _id = models.CharField(max_length=200, editable=False, unique=True)
    username = models.CharField(max_length=10)
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=2)
    courses = djmodels.JSONField(default=[], blank=True, null=True)
    status = djmodels.JSONField(default=[], blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # For User Parameterization
    pre_survey = djmodels.JSONField(default=[], blank=True, null=True)
    post_survey = djmodels.JSONField(default=[], blank=True, null=True)
    assessment_responses = djmodels.JSONField(default=[], blank=True, null=True)


    def __str__(self):
        return f"User(user_id={self.user_id}, name={self.name}, utorid={self.utorid}, user_role={self.user_role}, courses={self.courses})"
    
    class Meta:
        indexes = [
            models.Index(fields=['_id'], name='user_id_idx'),
            models.Index(fields=['username'], name='username_idx'),
        ]

class UserStatus(Model):
    _id = models.CharField(max_length=200, editable=False, unique=True)
    user_id = models.CharField(max_length=100)
    deployment_id = models.CharField(max_length=200)
    model_id = models.CharField(max_length=100)
    condition_id = models.CharField(max_length=100)
    status = models.BooleanField(default=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)

class UserStatistic(models.Model):
    
    _id = models.CharField(max_length=200, editable=False, unique=True)
    user_id = models.CharField(max_length=100)
    operation = models.CharField(max_length=100)
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['_id'], name='user_statistic_id_idx'),
            models.Index(fields=['user_id'], name='user_statistic_user_id_idx'),
        ]