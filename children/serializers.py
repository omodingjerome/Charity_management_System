"""
Serializers for Charity Management System - Children App
"""
from rest_framework import serializers
from .models import Child, Household, Caregiver, School, Project, Survey, SurveyQuestion, SurveyResponse, SurveyAnswer


class SchoolSerializer(serializers.ModelSerializer):
    """Serializer for School model"""
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = School
        fields = [
            'id', 'name', 'location', 'level', 'contact_phone',
            'children_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_children_count(self, obj):
        return obj.children.count()


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model"""
    enrolled_children_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'start_date', 'end_date',
            'is_active', 'enrolled_children_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_enrolled_children_count(self, obj):
        return obj.enrolled_children.count()


class CaregiverSerializer(serializers.ModelSerializer):
    """Serializer for Caregiver model"""
    children_count = serializers.SerializerMethodField()
    display_name = serializers.CharField(source='name', read_only=True)

    class Meta:
        model = Caregiver
        fields = [
            'id', 'name', 'relationship', 'phone', 'email', 'national_id',
            'has_disability', 'is_employed', 'occupation', 'display_name',
            'children_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_children_count(self, obj):
        return obj.children.count()

    def validate_child_id(self, value):
        """Validate national ID format if provided"""
        if value and len(value) < 5:
            raise serializers.ValidationError("National ID must be at least 5 characters")
        return value


class HouseholdSerializer(serializers.ModelSerializer):
    """Serializer for Household model"""
    children_detail = serializers.SerializerMethodField()
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = Household
        fields = [
            'id', 'household_name', 'number_of_people', 'main_income_source',
            'consistent_income_6months', 'children_under_18', 'is_savings_group_member',
            'residence_type', 'estimated_monthly_income', 'household_assets',
            'can_pay_emergency', 'children_detail', 'children_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_children_detail(self, obj):
        children = obj.children.all()[:5]  # Limit to 5 for list views
        return ChildListSerializer(children, many=True).data

    def get_children_count(self, obj):
        return obj.children.count()

    def validate_estimated_monthly_income(self, value):
        """Validate income is non-negative"""
        if value < 0:
            raise serializers.ValidationError("Income cannot be negative")
        return value


class ChildListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for child list views"""
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    school_name = serializers.CharField(source='school.name', read_only=True, allow_null=True)
    household_name = serializers.CharField(source='household.household_name', read_only=True)

    class Meta:
        model = Child
        fields = [
            'id', 'child_id', 'first_name', 'last_name', 'full_name',
            'date_of_birth', 'age', 'profile_photo', 'school_name',
            'household_name', 'is_active', 'registration_date'
        ]


class ChildSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for Child model with full details
    """
    # Read-only computed fields
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    
    # Nested serializers for related objects
    school = SchoolSerializer(read_only=True)
    school_id = serializers.PrimaryKeyRelatedField(
        queryset=School.objects.all(),
        source='school',
        write_only=True,
        required=False,
        allow_null=True
    )
    household = HouseholdSerializer(read_only=True)
    household_id = serializers.PrimaryKeyRelatedField(
        queryset=Household.objects.all(),
        source='household',
        write_only=True,
        required=False
    )
    caregivers = CaregiverSerializer(many=True, read_only=True)
    caregiver_ids = serializers.PrimaryKeyRelatedField(
        queryset=Caregiver.objects.all(),
        source='caregivers',
        many=True,
        write_only=True,
        required=False
    )
    projects = ProjectSerializer(many=True, read_only=True)
    project_ids = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        source='projects',
        many=True,
        write_only=True,
        required=False
    )

    class Meta:
        model = Child
        fields = [
            # Personal Information
            'id', 'child_id', 'first_name', 'last_name', 'full_name',
            'date_of_birth', 'age', 'profile_photo',
            
            # Medical Information
            'chronic_medical_condition',
            
            # Education Information
            'school', 'school_id',
            
            # Financial Support Information
            'income_provider', 'education_payer', 'medical_payer',
            
            # Relationships
            'household', 'household_id',
            'caregivers', 'caregiver_ids',
            'projects', 'project_ids',
            
            # Additional Information
            'notes', 'is_active', 'registration_date', 'updated_at'
        ]
        read_only_fields = [
            'id', 'full_name', 'age', 'registration_date', 'updated_at'
        ]

    def validate_child_id(self, value):
        """Validate and format child ID"""
        value = value.upper().strip()
        
        # Check uniqueness excluding current instance
        instance = self.instance
        if instance and instance.child_id == value:
            return value
            
        if Child.objects.filter(child_id=value).exists():
            raise serializers.ValidationError(
                f"Child with ID '{value}' already exists"
            )
        return value

    def validate_date_of_birth(self, value):
        """Validate date of birth is not in the future and age is reasonable"""
        from datetime import date
        today = date.today()
        
        if value > today:
            raise serializers.ValidationError("Date of birth cannot be in the future")
        
        # Calculate age
        age = today.year - value.year
        if (today.month, today.day) < (value.month, value.day):
            age -= 1
        
        if age > 25:
            raise serializers.ValidationError(
                f"Age {age} seems unreasonable for a child in scholarship program"
            )
        
        return value

    def validate(self, attrs):
        """Cross-field validation"""
        # Ensure household is provided for new objects
        if not self.instance and 'household' not in attrs and 'household_id' not in attrs:
            raise serializers.ValidationError({
                'household': 'Household is required'
            })
        return attrs


class ChildCreateSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for creating new children
    Handles nested household and caregiver creation
    """
    # Allow nested creation of household
    household_data = HouseholdSerializer(write_only=True, required=False)
    caregiver_data = CaregiverSerializer(write_only=True, many=True, required=False)

    class Meta:
        model = Child
        fields = [
            'child_id', 'first_name', 'last_name', 'date_of_birth',
            'profile_photo', 'chronic_medical_condition', 'school',
            'income_provider', 'education_payer', 'medical_payer',
            'household', 'household_data', 'caregivers', 'caregiver_data',
            'projects', 'notes'
        ]

    def create(self, validated_data):
        household_data = validated_data.pop('household_data', None)
        caregiver_data = validated_data.pop('caregiver_data', None)
        
        # Create household if provided
        if household_data:
            household = Household.objects.create(**household_data)
            validated_data['household'] = household
        
        # Create child instance
        child = Child.objects.create(**validated_data)
        
        # Create caregivers if provided
        if caregiver_data:
            for caregiver_info in caregiver_data:
                caregiver = Caregiver.objects.create(**caregiver_info)
                child.caregivers.add(caregiver)
        
        return child


# ============== Survey Serializers ==============

class SurveyQuestionSerializer(serializers.ModelSerializer):
    """Serializer for Survey Question model"""
    choices_list = serializers.SerializerMethodField()
    
    class Meta:
        model = SurveyQuestion
        fields = [
            'id', 'question_text', 'question_type', 'choices', 
            'choices_list', 'is_required', 'order'
        ]
    
    def get_choices_list(self, obj):
        return obj.get_choices_list()


class SurveySerializer(serializers.ModelSerializer):
    """Serializer for Survey model"""
    questions = SurveyQuestionSerializer(many=True, read_only=True)
    response_count = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Survey
        fields = [
            'id', 'title', 'description', 'survey_type', 'is_active', 
            'created_by', 'created_by_name', 'created_at', 'updated_at', 
            'deadline', 'questions', 'response_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_response_count(self, obj):
        return obj.responses.count()


class SurveyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating surveys with questions"""
    questions = SurveyQuestionSerializer(many=True, required=False)
    
    class Meta:
        model = Survey
        fields = [
            'title', 'description', 'survey_type', 'is_active', 
            'deadline', 'questions'
        ]
    
    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        validated_data['created_by'] = self.context['request'].user
        
        survey = Survey.objects.create(**validated_data)
        
        for idx, question_data in enumerate(questions_data):
            question_data['order'] = question_data.get('order', idx)
            SurveyQuestion.objects.create(survey=survey, **question_data)
        
        return survey


class SurveyAnswerSerializer(serializers.ModelSerializer):
    """Serializer for Survey Answer model"""
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    
    class Meta:
        model = SurveyAnswer
        fields = ['id', 'question', 'question_text', 'answer_text']


class SurveyResponseSerializer(serializers.ModelSerializer):
    """Serializer for Survey Response model"""
    answers = SurveyAnswerSerializer(many=True, read_only=True)
    respondent_name = serializers.CharField(source='respondent.full_name', read_only=True)
    survey_title = serializers.CharField(source='survey.title', read_only=True)
    
    class Meta:
        model = SurveyResponse
        fields = [
            'id', 'survey', 'survey_title', 'respondent', 'respondent_name',
            'child', 'household', 'submitted_at', 'is_complete', 'answers'
        ]


class SurveyResponseCreateSerializer(serializers.ModelSerializer):
    """Serializer for submitting survey responses"""
    answers = serializers.ListField(write_only=True)
    
    class Meta:
        model = SurveyResponse
        fields = ['survey', 'child', 'household', 'answers']
    
    def create(self, validated_data):
        answers_data = validated_data.pop('answers', [])
        volunteer = self.context['request'].user.volunteer
        
        survey_response = SurveyResponse.objects.create(
            survey=validated_data['survey'],
            respondent=volunteer,
            child=validated_data.get('child'),
            household=validated_data.get('household'),
            is_complete=True
        )
        
        # Create answers
        for answer_data in answers_data:
            SurveyAnswer.objects.create(
                response=survey_response,
                question_id=answer_data.get('question_id'),
                answer_text=answer_data.get('answer_text', '')
            )
        
        return survey_response
