"""
Django Admin Configuration for Children App
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Child, Household, Caregiver, School, Project, Survey, SurveyQuestion, SurveyResponse, SurveyAnswer


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'location', 'contact_phone', 'children_count']
    list_filter = ['level']
    search_fields = ['name', 'location']
    ordering = ['name']

    def children_count(self, obj):
        return obj.children.count()
    children_count.short_description = 'Children'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_active', 'enrolled_count']
    list_filter = ['is_active', 'start_date']
    search_fields = ['name', 'description']
    ordering = ['-start_date']
    date_hierarchy = 'start_date'

    def enrolled_count(self, obj):
        return obj.enrolled_children.count()
    enrolled_count.short_description = 'Enrolled'


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = [
        'household_name', 'number_of_people', 'residence_type',
        'estimated_monthly_income', 'is_savings_group_member', 'children_count'
    ]
    list_filter = ['residence_type', 'is_savings_group_member', 'consistent_income_6months']
    search_fields = ['household_name']
    ordering = ['-created_at']

    def children_count(self, obj):
        return obj.children.count()
    children_count.short_description = 'Children'


@admin.register(Caregiver)
class CaregiverAdmin(admin.ModelAdmin):
    list_display = ['name', 'relationship', 'phone', 'email', 'has_disability', 'children_count']
    list_filter = ['relationship', 'has_disability', 'is_employed']
    search_fields = ['name', 'phone', 'email', 'national_id']
    ordering = ['name']

    def children_count(self, obj):
        return obj.children.count()
    children_count.short_description = 'Children'


class CaregiverInline(admin.TabularInline):
    model = Child.caregivers.through
    extra = 1


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    """Admin configuration for Child model"""
    
    list_display = [
        'child_id', 'first_name', 'last_name', 'age_display',
        'school', 'household_link', 'photo_thumbnail', 'is_active'
    ]
    list_filter = ['is_active', 'school', 'registration_date']
    search_fields = ['first_name', 'last_name', 'child_id', 'household__household_name']
    ordering = ['-registration_date']
    date_hierarchy = 'registration_date'
    
    # Fieldsets for organized form display
    fieldsets = (
        ('Personal Information', {
            'fields': (
                ('first_name', 'last_name'),
                ('date_of_birth', 'child_id'),
                'profile_photo'
            )
        }),
        ('Medical & Education', {
            'fields': (
                'chronic_medical_condition',
                'school'
            )
        }),
        ('Financial Support', {
            'fields': (
                'income_provider',
                'education_payer',
                'medical_payer'
            )
        }),
        ('Relationships', {
            'fields': (
                'household',
                'caregivers',
                'projects'
            )
        }),
        ('Status', {
            'fields': ('is_active', 'notes')
        }),
    )
    
    # Filter horizontal for many-to-many fields
    filter_horizontal = ['caregivers', 'projects']
    
    # Raw ID fields for foreign keys (better performance with many records)
    raw_id_fields = ['household', 'school']
    
    # List select for better performance
    list_select_related = ['school', 'household']
    
    readonly_fields = ['registration_date', 'updated_at']
    
    def age_display(self, obj):
        """Display age with color coding"""
        age = obj.age
        if age < 10:
            color = 'green'
        elif age < 15:
            color = 'orange'
        else:
            color = 'blue'
        return format_html('<span style="color: {};">{} years</span>', color, age)
    age_display.short_description = 'Age'
    
    def photo_thumbnail(self, obj):
        """Display thumbnail of profile photo"""
        if obj.profile_photo:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius: 50%;" />',
                obj.profile_photo.url
            )
        return '-'
    photo_thumbnail.short_description = 'Photo'
    
    def household_link(self, obj):
        """Link to household detail"""
        if obj.household:
            return format_html(
                '<a href="/admin/children/household/{}/change/">{}</a>',
                obj.household.id,
                obj.household.household_name
            )
        return '-'
    household_link.short_description = 'Household'
    
    # Custom actions
    actions = ['mark_as_active', 'mark_as_inactive']
    
    def mark_as_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} children marked as active.')
    mark_as_active.short_description = 'Mark selected children as active'
    
    def mark_as_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} children marked as inactive.')
    mark_as_inactive.short_description = 'Mark selected children as inactive'


# ============== Survey Admin Classes ==============

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    """Admin configuration for Survey model"""
    list_display = ['title', 'survey_type', 'is_active', 'created_by', 'created_at', 'deadline', 'response_count']
    list_filter = ['survey_type', 'is_active', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    
    def response_count(self, obj):
        return obj.responses.count()
    response_count.short_description = 'Responses'


class SurveyQuestionInline(admin.TabularInline):
    """Inline admin for survey questions"""
    model = SurveyQuestion
    extra = 1
    fields = ['question_text', 'question_type', 'choices', 'is_required', 'order']


@admin.register(SurveyQuestion)
class SurveyQuestionAdmin(admin.ModelAdmin):
    """Admin configuration for Survey Question model"""
    list_display = ['question_text', 'survey', 'question_type', 'is_required', 'order']
    list_filter = ['question_type', 'survey']
    search_fields = ['question_text']
    ordering = ['survey', 'order']


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    """Admin configuration for Survey Response model"""
    list_display = ['survey', 'respondent', 'child', 'submitted_at', 'is_complete']
    list_filter = ['survey', 'is_complete', 'submitted_at']
    search_fields = ['survey__title', 'respondent__first_name', 'respondent__last_name']
    ordering = ['-submitted_at']
    date_hierarchy = 'submitted_at'
    readonly_fields = ['submitted_at']
    raw_id_fields = ['respondent', 'child', 'household']


@admin.register(SurveyAnswer)
class SurveyAnswerAdmin(admin.ModelAdmin):
    """Admin configuration for Survey Answer model"""
    list_display = ['response', 'question', 'answer_text']
    search_fields = ['answer_text', 'question__question_text']
    raw_id_fields = ['response', 'question']
