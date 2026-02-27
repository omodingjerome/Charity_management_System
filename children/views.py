"""
Views for Charity Management System - Children App
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from .models import Child, Household, Caregiver, School, Project, Survey, SurveyQuestion, SurveyResponse, SurveyAnswer
from .serializers import (
    ChildSerializer, ChildListSerializer, ChildCreateSerializer,
    HouseholdSerializer, CaregiverSerializer,
    SchoolSerializer, ProjectSerializer,
    SurveySerializer, SurveyCreateSerializer, SurveyQuestionSerializer,
    SurveyResponseSerializer, SurveyResponseCreateSerializer, SurveyAnswerSerializer
)


class ChildViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing children in the scholarship program.
    Provides CRUD operations and additional actions for child management.
    """
    queryset = Child.objects.select_related(
        'school', 'household'
    ).prefetch_related(
        'caregivers', 'projects'
    ).all()
    
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    
    # Filter fields
    filterset_fields = {
        'is_active': ['exact'],
        'school__id': ['exact'],
        'household__id': ['exact'],
        'date_of_birth': ['gte', 'lte', 'exact'],
    }
    
    # Search fields
    search_fields = [
        'first_name', 'last_name', 'child_id',
        'household__household_name'
    ]
    
    # Ordering fields
    ordering_fields = [
        'registration_date', 'date_of_birth', 'last_name', 'first_name'
    ]
    ordering = ['-registration_date']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ChildListSerializer
        if self.action == 'create':
            return ChildCreateSerializer
        return ChildSerializer
    
    def get_permissions(self):
        """Allow public access for list/detail, require auth for mutations"""
        if self.action in ['list', 'retrieve', 'directory']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def directory(self, request):
        """
        Children Directory - public listing endpoint
        Returns active children with basic information
        """
        children = self.queryset.filter(is_active=True)
        
        # Apply filters
        school_id = request.query_params.get('school_id')
        if school_id:
            children = children.filter(school_id=school_id)
        
        # Age range filter
        min_age = request.query_params.get('min_age')
        max_age = request.query_params.get('max_age')
        
        serializer = ChildListSerializer(children, many=True)
        return Response({
            'count': children.count(),
            'children': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def enroll_project(self, request, pk=None):
        """Enroll child in a project"""
        child = self.get_object()
        project_id = request.data.get('project_id')
        
        if not project_id:
            return Response(
                {'error': 'project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            project = Project.objects.get(id=project_id)
            child.projects.add(project)
            return Response({'status': 'enrolled'})
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def unenroll_project(self, request, pk=None):
        """Unenroll child from a project"""
        child = self.get_object()
        project_id = request.data.get('project_id')
        
        if not project_id:
            return Response(
                {'error': 'project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            project = Project.objects.get(id=project_id)
            child.projects.remove(project)
            return Response({'status': 'unenrolled'})
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get statistics about children"""
        total = Child.objects.count()
        active = Child.objects.filter(is_active=True).count()
        
        # Age distribution
        from datetime import date
        today = date.today()
        
        stats = {
            'total_children': total,
            'active_children': active,
            'inactive_children': total - active,
            'by_age_group': {
                'under_5': Child.objects.filter(
                    date_of_birth__gte=today.replace(year=today.year-5)
                ).count(),
                '5_to_10': Child.objects.filter(
                    date_of_birth__lt=today.replace(year=today.year-5),
                    date_of_birth__gte=today.replace(year=today.year-10)
                ).count(),
                '11_to_15': Child.objects.filter(
                    date_of_birth__lt=today.replace(year=today.year-10),
                    date_of_birth__gte=today.replace(year=today.year-15)
                ).count(),
                'over_15': Child.objects.filter(
                    date_of_birth__lt=today.replace(year=today.year-15)
                ).count(),
            }
        }
        
        return Response(stats)


class HouseholdViewSet(viewsets.ModelViewSet):
    """ViewSet for managing households"""
    queryset = Household.objects.all()
    serializer_class = HouseholdSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['residence_type', 'is_savings_group_member']
    search_fields = ['household_name']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        """Get all children in a household"""
        household = self.get_object()
        children = household.children.all()
        serializer = ChildListSerializer(children, many=True)
        return Response(serializer.data)


class CaregiverViewSet(viewsets.ModelViewSet):
    """ViewSet for managing caregivers"""
    queryset = Caregiver.objects.all()
    serializer_class = CaregiverSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['relationship', 'has_disability', 'is_employed']
    search_fields = ['name', 'phone', 'email']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]


class SchoolViewSet(viewsets.ModelViewSet):
    """ViewSet for managing schools"""
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['level']
    search_fields = ['name', 'location']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]


class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for managing projects/events"""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Filter active projects by default for list action"""
        queryset = Project.objects.all()
        if self.action == 'list':
            show_inactive = self.request.query_params.get('show_inactive')
            if not show_inactive:
                queryset = queryset.filter(is_active=True)
        return queryset


# ============== Survey Viewsets ==============

class SurveyViewSet(viewsets.ModelViewSet):
    """ViewSet for managing surveys (admin creates, volunteers view/take)"""
    queryset = Survey.objects.prefetch_related('questions').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['survey_type', 'is_active']
    search_fields = ['title', 'description']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SurveyCreateSerializer
        return SurveySerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    @action(detail=True, methods=['get'])
    def take(self, request, pk=None):
        """Get survey details for taking (volunteers)"""
        survey = self.get_object()
        serializer = SurveySerializer(survey)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get available surveys for volunteers"""
        surveys = Survey.objects.filter(is_active=True)
        serializer = SurveySerializer(surveys, many=True)
        return Response(serializer.data)


class SurveyQuestionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing survey questions"""
    queryset = SurveyQuestion.objects.all()
    serializer_class = SurveyQuestionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['survey']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]


class SurveyResponseViewSet(viewsets.ModelViewSet):
    """ViewSet for managing survey responses"""
    queryset = SurveyResponse.objects.select_related(
        'survey', 'respondent', 'child', 'household'
    ).prefetch_related('answers').all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SurveyResponseCreateSerializer
        return SurveyResponseSerializer
    
    def get_permissions(self):
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        # Admins see all responses, volunteers see only their own
        if user.is_staff:
            return SurveyResponse.objects.all()
        # Try to get volunteer
        try:
            volunteer = user.volunteer
            return SurveyResponse.objects.filter(respondent=volunteer)
        except:
            return SurveyResponse.objects.none()
    
    @action(detail=False, methods=['get'])
    def my_responses(self, request):
        """Get current user's survey responses"""
        try:
            volunteer = request.user.volunteer
            responses = SurveyResponse.objects.filter(respondent=volunteer)
            serializer = SurveyResponseSerializer(responses, many=True)
            return Response(serializer.data)
        except:
            return Response([])
