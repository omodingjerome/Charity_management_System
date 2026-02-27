"""
URL Configuration for Children App
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ChildViewSet, HouseholdViewSet, CaregiverViewSet,
    SchoolViewSet, ProjectViewSet,
    SurveyViewSet, SurveyQuestionViewSet, SurveyResponseViewSet
)

app_name = 'api'  # Use 'api' namespace to avoid conflict with HTML URLs

router = DefaultRouter()
router.register(r'children', ChildViewSet, basename='child')
router.register(r'households', HouseholdViewSet, basename='household')
router.register(r'caregivers', CaregiverViewSet, basename='caregiver')
router.register(r'schools', SchoolViewSet, basename='school')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'surveys', SurveyViewSet, basename='survey')
router.register(r'survey-questions', SurveyQuestionViewSet, basename='survey-question')
router.register(r'survey-responses', SurveyResponseViewSet, basename='survey-response')

urlpatterns = [
    path('', include(router.urls)),
]
