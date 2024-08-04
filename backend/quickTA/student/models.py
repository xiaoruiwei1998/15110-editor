from datetime import datetime 
from django.db import models
from django.utils.timezone import now
import djongo.models as djmodels

from users.model import User
from course.models import Course
from pydantic import BaseModel

# Create your models here.
class Conversation(models.Model):
    _id = models.CharField(max_length=100)
    conversation_name = models.CharField(max_length=100, blank=True, null=True)
    course_id = models.CharField(max_length=100)
    model_id = models.CharField(max_length=100)
    user_id = models.CharField(max_length=50)  
    start_time = models.DateTimeField(default=now)
    end_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=1, default='A')
    reported = models.BooleanField(default=False)
    conversation_log = djmodels.JSONField(default=list)
    forced_inactive = models.CharField(max_length=1, default="")
    graded = models.BooleanField(default=False)

    def __str__(self):
        return f"[{str(self.course_id)}] {str(self.user_id)} - Conversation {str(self.conversation_id)}"
    
    def to_dict(self):
        user, course = None, None
        try:
            user = User.objects.get(user_id=self.user_id)
            course = Course.objects.get(course_id=self.course_id)
        except: pass
        return {
            "course_name": course.course_name if course else "Unknown",
            "course_id": self.course_id,
            "user_id": self.user_id,
            "model_id": self.model_id,
            "user_name": user.name if user else "Anonymous",
            "utorid": user.utorid if user else "Anonymous",
            "conversation_id": str(self._id),
            "start_time": self.start_time,
            "end_time": self.end_time,
            "status": self.status,
            "reported": self.reported,
            "reported": self.reported,
            "graded": self.graded,
        }

class Chatlog(models.Model):
    _id = models.CharField(max_length=100)
    conversation_id = models.CharField(max_length=100)
    time = models.DateTimeField(default=datetime.now)
    is_user = models.BooleanField()
    chatlog = models.TextField(max_length = 3000)
    delta = models.DurationField(blank=True, null=True)

    def __str__(self):
        return f"[{str(self.conversation)}] Chatlog - {str(self._id)} {self.chatlog}"
    
    def to_dict(self, show_alias=False):

        if show_alias:
            convo = Conversation.objects.get(conversation_id=self.conversation_id)
            user = User.objects.get(user_id=convo.user_id)
            return {
                "chatlog_id": str(self._id),
                "conversation_id": self.conversation_id,
                "time": self.time,
                "speaker": user.name if self.is_user else "Agent",
                "chatlog": self.chatlog,
                "delta": str(self.delta) if self.delta else None
            }
        return {
            "chatlog_id": str(self._id),
            "conversation_id": self.conversation_id,
            "time": self.time,
            "is_user": self.is_user,
            "chatlog": self.chatlog,
            "delta": str(self.delta) if self.delta else None
        }

class Report(models.Model): 
    _id = models.CharField(max_length=100)
    conversation_id = models.CharField(max_length=100)
    time = models.DateTimeField(default=now)
    status = models.CharField(max_length=1, default='O')
    msg = models.TextField(max_length=3000)

    def __str__(self):
        return f"[{str(self.conversation)}] {self.msg}"
    
    def to_dict(self):
        conversation = Conversation.objects.get(conversation_id=self.conversation_id)
        user = User.objects.get(user_id=conversation.user_id)

        return {
            "course_id": conversation.course_id,
            "conversation_id": self.conversation_id,
            "user_id": user.user_id,
            "user_name": user.name,
            "utorid": user.utorid,
            "time": self.time,
            "status": self.status,
            "msg": self.msg
        }


class Feedback(models.Model):
    _id = models.CharField(max_length=100)
    conversation_id = models.CharField(max_length=100)
    rating = models.FloatField()
    feedback_msg = models.TextField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return f"[{str(self.conversation)}] Feedback"
    
    def to_dict(self):
        conversation = None
        try:
            conversation = Conversation.objects.get(conversation_id=self.conversation_id)
        except: pass

        return {
            "_id": self._id,
            "course_id": conversation.course_id if conversation else "Unknown",
            "rating": self.rating,
            "feedback_msg": self.feedback_msg
        }

class ConversationNotes(models.Model):
    _id = models.CharField(max_length=100)
    conversation_id = models.CharField(max_length=100)
    notes = djmodels.JSONField(default=dict)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

