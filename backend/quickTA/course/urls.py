from django.urls import path
from .views import *

app_name = 'course_api'

urlpatterns = [
    path('', CourseView.as_view()),
    path('/all', CourseList.as_view()),
    path('/list', CourseMultipleList.as_view()),
    path('/enroll', CourseEnrollment.as_view()),
    path('/users', CourseUserList.as_view()),
    path('/models', CourseModelList.as_view()),
]