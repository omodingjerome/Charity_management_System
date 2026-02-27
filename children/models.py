"""
Children models for Charity Management System
"""
from datetime import date
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class School(models.Model):
    """School model - stores educational institutions"""
    name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=255, blank=True)
    level = models.CharField(
        max_length=50,
        choices=[
            ('primary', 'Primary'),
            ('secondary', 'Secondary'),
            ('tertiary', 'Tertiary'),
            ('vocational', 'Vocational'),
        ],
        default='primary'
    )
    contact_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Schools'

    def __str__(self):
        return self.name


class Project(models.Model):
    """Project/Event model - scholarship programs, events, interventions"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name


class Volunteer(models.Model):
    """Volunteer model - stores volunteer information"""
    VOLUNTEER_ROLES = [
        ('education', 'Education Mentor'),
        ('healthcare', 'Healthcare'),
        ('counseling', 'Counseling'),
        ('logistics', 'Logistics'),
        ('fundraising', 'Fundraising'),
        ('general', 'General Volunteer'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
    ]
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    role = models.CharField(max_length=20, choices=VOLUNTEER_ROLES, default='general')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    photo = models.ImageField(upload_to='volunteers/photos/', blank=True, null=True)
    hours_contributed = models.FloatField(default=0)
    date_joined = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['status', 'role']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Household(models.Model):
    """Household model - stores household information"""
    RESIDENCE_TYPE_CHOICES = [
        ('owned', 'Owned'),
        ('rented', 'Rented'),
        ('informal', 'Informal/Slum'),
        ('other', 'Other'),
    ]

    household_name = models.CharField(max_length=255)
    number_of_people = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    main_income_source = models.CharField(max_length=255, blank=True)
    consistent_income_6months = models.BooleanField(default=False)
    children_under_18 = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    is_savings_group_member = models.BooleanField(default=False, verbose_name='Part of savings group')
    residence_type = models.CharField(
        max_length=20,
        choices=RESIDENCE_TYPE_CHOICES,
        default='informal'
    )
    estimated_monthly_income = models.FloatField(
        default=0,
        help_text='Estimated monthly household income'
    )
    household_assets = models.TextField(blank=True, help_text='List household assets')
    can_pay_emergency = models.BooleanField(default=False, verbose_name='Can pay emergency expense')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Households'

    def __str__(self):
        return f"Household: {self.household_name}"


class Caregiver(models.Model):
    """Caregiver model - stores parent/guardian information"""
    RELATIONSHIP_CHOICES = [
        ('mother', 'Mother'),
        ('father', 'Father'),
        ('grandmother', 'Grandmother'),
        ('grandfather', 'Grandfather'),
        ('aunt', 'Aunt'),
        ('uncle', 'Uncle'),
        ('sibling', 'Sibling'),
        ('other_relative', 'Other Relative'),
        ('non_relative', 'Non-Relative'),
    ]

    name = models.CharField(max_length=255)
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    national_id = models.CharField(max_length=50, blank=True, verbose_name='National ID')
    has_disability = models.BooleanField(default=False, verbose_name='Has disability')
    is_employed = models.BooleanField(default=False)
    occupation = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_relationship_display()})"


class Child(models.Model):
    """Child model - main entity for scholarship program"""

    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    profile_photo = models.ImageField(
        upload_to='children/photos/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text='Upload a recent photo of the child'
    )
    child_id = models.CharField(
        max_length=50,
        unique=True,
        help_text='Unique child identifier'
    )

    # Medical Information
    chronic_medical_condition = models.TextField(
        blank=True,
        verbose_name='Chronic medical condition',
        help_text='Any ongoing medical conditions'
    )

    # Education Information
    school = models.ForeignKey(
        School,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )

    # Financial Support Information
    income_provider = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Who provides most household income',
        help_text='Primary income provider for the household'
    )
    education_payer = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Who pays for education',
        help_text='Person/organization paying for education'
    )
    medical_payer = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Who pays for medical bills',
        help_text='Person/organization paying for medical expenses'
    )

    # Household Relationship
    household = models.ForeignKey(
        Household,
        on_delete=models.CASCADE,
        related_name='children'
    )

    # Caregivers (can have multiple)
    caregivers = models.ManyToManyField(
        Caregiver,
        related_name='children',
        blank=True
    )

    # Projects/Events enrollment
    projects = models.ManyToManyField(
        Project,
        related_name='enrolled_children',
        blank=True
    )

    # Additional Information
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-registration_date']
        indexes = [
            models.Index(fields=['child_id']),
            models.Index(fields=['date_of_birth']),
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['registration_date']),
        ]

    def __str__(self):
        return f"{self.child_id}: {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        """Return full name of the child"""
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        """Calculate age from date of birth"""
        today = date.today()
        birth_date = self.date_of_birth
        age = today.year - birth_date.year
        # Adjust if birthday hasn't occurred this year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age

    @property
    def age_years(self):
        """Return age in years (for display)"""
        return self.age

    def save(self, *args, **kwargs):
        """Override save to ensure data consistency"""
        # Clean up child_id
        if self.child_id:
            self.child_id = self.child_id.upper().strip()
        super().save(*args, **kwargs)


class Survey(models.Model):
    """Survey model - for creating survey forms (admin only)"""
    SURVEY_TYPES = [
        ('household', 'Household Assessment'),
        ('child', 'Child Assessment'),
        ('feedback', 'Feedback Survey'),
        ('evaluation', 'Program Evaluation'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    survey_type = models.CharField(max_length=20, choices=SURVEY_TYPES, default='other')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_surveys'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Survey'
        verbose_name_plural = 'Surveys'
    
    def __str__(self):
        return self.title


class SurveyQuestion(models.Model):
    """Survey questions - linked to a survey"""
    QUESTION_TYPES = [
        ('text', 'Short Text'),
        ('textarea', 'Long Text'),
        ('choice', 'Single Choice'),
        ('multiple', 'Multiple Choice'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('yes_no', 'Yes/No'),
    ]
    
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='text')
    choices = models.TextField(
        blank=True, 
        help_text='Comma-separated choices for choice/multiple question types'
    )
    is_required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.survey.title} - Q{self.order}: {self.question_text[:50]}"
    
    def get_choices_list(self):
        """Return choices as a list"""
        if self.choices:
            return [c.strip() for c in self.choices.split(',')]
        return []


class SurveyResponse(models.Model):
    """Survey responses - submitted by volunteers"""
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    respondent = models.ForeignKey(
        Volunteer, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='survey_responses'
    )
    child = models.ForeignKey(
        Child, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='survey_responses'
    )
    household = models.ForeignKey(
        Household,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='survey_responses'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_complete = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Survey Response'
        verbose_name_plural = 'Survey Responses'
    
    def __str__(self):
        return f"Response to {self.survey.title} by {self.respondent}"


class SurveyAnswer(models.Model):
    """Individual answers to survey questions"""
    response = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('response', 'question')
    
    def __str__(self):
        return f"Answer to: {self.question.question_text[:30]}..."
