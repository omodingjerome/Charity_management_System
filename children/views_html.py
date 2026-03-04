"""
Template Views for Charity Management System - HTML Frontend
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Sum
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from .models import Child, Household, Caregiver, School, Project, Volunteer, Survey, SurveyQuestion, SurveyResponse, SurveyAnswer
from django.http import JsonResponse
from django.contrib.auth.models import User


from datetime import date, timedelta


def login_view(request):
    """User login page"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'children/login.html')


def signup_view(request):
    """User registration page"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user_type = request.POST.get('user_type', 'volunteer')
        
        # Validation
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'children/signup.html')
        
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return render(request, 'children/signup.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'children/signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'children/signup.html')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create volunteer profile if volunteer
        if user_type == 'volunteer':
            Volunteer.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=request.POST.get('phone', ''),
                role=request.POST.get('role', 'general'),
                status='active'
            )
        else:
            # Make admin
            user.is_staff = True
            user.save()
        
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('login')
    
    return render(request, 'children/signup.html')


def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


def home(request):
    """Home page with dashboard"""
    total_children = Child.objects.count()
    active_children = Child.objects.filter(is_active=True).count()
    total_households = Household.objects.count()
    
    # Volunteer stats
    total_volunteers = Volunteer.objects.count()
    active_volunteers = Volunteer.objects.filter(status='active').count()
    
    # New volunteers this month
    today = date.today()
    first_day_of_month = today.replace(day=1)
    new_volunteers_month = Volunteer.objects.filter(date_joined__gte=first_day_of_month).count()
    
    # Total hours
    total_hours = Volunteer.objects.aggregate(total=Sum('hours_contributed'))['total'] or 0
    
    recent_children = Child.objects.select_related('school').order_by('-registration_date')[:5]
    
    context = {
        'total_children': total_children,
        'active_children': active_children,
        'total_households': total_households,
        'total_volunteers': total_volunteers,
        'active_volunteers': active_volunteers,
        'new_volunteers_month': new_volunteers_month,
        'total_hours': total_hours,
        'recent_children': recent_children,
    }
    return render(request, 'children/home.html', context)


def children_directory(request):
    """Children Directory - List all children"""
    children_list = Child.objects.select_related('school', 'household').filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        children_list = children_list.filter(
            first_name__icontains=search_query
        ) | children_list.filter(
            last_name__icontains=search_query
        ) | children_list.filter(
            child_id__icontains=search_query
        )
    
    # Filter by school
    school_id = request.GET.get('school')
    if school_id:
        children_list = children_list.filter(school_id=school_id)
    
    # Pagination
    paginator = Paginator(children_list, 20)
    page_number = request.GET.get('page')
    children = paginator.get_page(page_number)
    
    schools = School.objects.all()
    
    context = {
        'children': children,
        'schools': schools,
        'search_query': search_query or '',
    }
    return render(request, 'children/directory.html', context)


def child_detail(request, pk):
    """Child Detail View"""
    child = get_object_or_404(Child.objects.select_related('school', 'household').prefetch_related('caregivers', 'projects'), pk=pk)
    return render(request, 'children/detail.html', {'child': child})


def add_child(request):
    """Add Child Record Form"""
    if request.method == 'POST':
        # Handle form submission
        # Only use provided child_id if not empty, otherwise signal will auto-generate
        child_id = request.POST.get('child_id', '').strip() or None
        
        child = Child(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            date_of_birth=request.POST.get('date_of_birth'),
            child_id=child_id,
            chronic_medical_condition=request.POST.get('chronic_medical_condition', ''),
            income_provider=request.POST.get('income_provider', ''),
            education_payer=request.POST.get('education_payer', ''),
            medical_payer=request.POST.get('medical_payer', ''),
        )
        
        # Handle household
        household_id = request.POST.get('household')
        if household_id:
            child.household_id = household_id
        
        # Handle school
        school_id = request.POST.get('school')
        if school_id:
            child.school_id = school_id
        
        try:
            child.save()
            messages.success(request, f'Child {child.full_name} added successfully!')
            return redirect(f'/children/{child.id}/')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    households = Household.objects.all()
    schools = School.objects.all()
    caregivers = Caregiver.objects.all()
    projects = Project.objects.all()
    
    context = {
        'households': households,
        'schools': schools,
        'caregivers': caregivers,
        'projects': projects,
    }
    return render(request, 'children/add_child.html', context)


def households_list(request):
    """Households List"""
    households = Household.objects.all()
    return render(request, 'children/households.html', {'households': households})


def add_household(request):
    """Add Household Form"""
    if request.method == 'POST':
        household = Household(
            household_name=request.POST.get('household_name'),
            number_of_people=int(request.POST.get('number_of_people', 1) or 1),
            main_income_source=request.POST.get('main_income_source', ''),
            consistent_income_6months='consistent_income_6months' in request.POST,
            children_under_18=int(request.POST.get('children_under_18', 0) or 0),
            is_savings_group_member='is_savings_group_member' in request.POST,
            residence_type=request.POST.get('residence_type', 'informal'),
            estimated_monthly_income=float(request.POST.get('estimated_monthly_income', 0) or 0),
            household_assets=request.POST.get('household_assets', ''),
            can_pay_emergency='can_pay_emergency' in request.POST,
        )
        household.save()
        messages.success(request, 'Household added successfully!')
        return redirect('households')
    
    return render(request, 'children/add_household.html')


def volunteers_list(request):
    """Volunteers List"""
    volunteers = Volunteer.objects.all()
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        volunteers = volunteers.filter(status=status_filter)
    
    # Filter by role
    role_filter = request.GET.get('role')
    if role_filter:
        volunteers = volunteers.filter(role=role_filter)
    
    # Search
    search = request.GET.get('search')
    if search:
        volunteers = volunteers.filter(
            models.Q(first_name__icontains=search) | 
            models.Q(last_name__icontains=search) |
            models.Q(email__icontains=search)
        )
    
    # Stats
    total_volunteers = Volunteer.objects.count()
    active_volunteers = Volunteer.objects.filter(status='active').count()
    
    context = {
        'volunteers': volunteers,
        'total_volunteers': total_volunteers,
        'active_volunteers': active_volunteers,
    }
    return render(request, 'children/volunteers.html', context)


def add_volunteer(request):
    """Add Volunteer Form"""
    if request.method == 'POST':
        volunteer = Volunteer(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            role=request.POST.get('role', 'general'),
            status=request.POST.get('status', 'active'),
            hours_contributed=float(request.POST.get('hours_contributed', 0) or 0),
            notes=request.POST.get('notes', ''),
        )
        volunteer.save()
        messages.success(request, f'Volunteer {volunteer.full_name} added successfully!')
        return redirect('/volunteers/')
    
    return render(request, 'children/add_volunteer.html')


# ============== Survey Views ==============

def surveys_list(request):
    """Surveys List - View all surveys (admin creates, volunteers view)"""
    # Get filter params
    survey_type = request.GET.get('type')
    status_filter = request.GET.get('status')
    
    surveys = Survey.objects.all().order_by('-created_at')
    
    if survey_type:
        surveys = surveys.filter(survey_type=survey_type)
    if status_filter == 'active':
        surveys = surveys.filter(is_active=True)
    elif status_filter == 'inactive':
        surveys = surveys.filter(is_active=False)
    
    # Add response counts
    for survey in surveys:
        survey.response_count = survey.responses.count()
    
    context = {
        'surveys': surveys,
        'survey_type': survey_type,
        'status_filter': status_filter,
    }
    return render(request, 'children/surveys.html', context)


def survey_detail(request, pk):
    """Survey Detail - View survey with questions"""
    survey = get_object_or_404(Survey.objects.prefetch_related('questions'), pk=pk)
    
    context = {
        'survey': survey,
    }
    return render(request, 'children/survey_detail.html', context)


def survey_create(request):
    """Create Survey Form (Admin only)"""
    if request.method == 'POST':
        # Create survey
        survey = Survey(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            survey_type=request.POST.get('survey_type', 'other'),
            is_active=request.POST.get('is_active') == 'on',
            deadline=request.POST.get('deadline') or None,
        )
        survey.save()
        
        # Add questions
        question_texts = request.POST.getlist('question_text[]')
        question_types = request.POST.getlist('question_type[]')
        question_choices = request.POST.getlist('question_choices[]')
        is_required = request.POST.getlist('is_required[]')
        
        for idx, q_text in enumerate(question_texts):
            if q_text.strip():
                SurveyQuestion.objects.create(
                    survey=survey,
                    question_text=q_text,
                    question_type=question_types[idx] if idx < len(question_types) else 'text',
                    choices=question_choices[idx] if idx < len(question_choices) else '',
                    is_required=str(idx) in is_required,
                    order=idx
                )
        
        messages.success(request, f'Survey "{survey.title}" created successfully!')
        return redirect('surveys')
    
    return render(request, 'children/survey_create.html')


def survey_take(request, pk):
    """Take Survey Form (Volunteers)"""
    survey = get_object_or_404(Survey.objects.prefetch_related('questions'), pk=pk)
    
    # Get children and households for selection
    children = Child.objects.all()
    households = Household.objects.all()
    
    if request.method == 'POST':
        # Get or create volunteer from user
        try:
            volunteer = request.user.volunteer
        except:
            messages.error(request, 'You must be a volunteer to take surveys.')
            return redirect(f'/surveys/{pk}/take/')
        
        # Create response
        response = SurveyResponse(
            survey=survey,
            respondent=volunteer,
            child_id=request.POST.get('child') or None,
            household_id=request.POST.get('household') or None,
            is_complete=True
        )
        response.save()
        
        # Save answers
        for question in survey.questions.all():
            answer_text = request.POST.get(f'question_{question.id}', '')
            SurveyAnswer.objects.create(
                response=response,
                question=question,
                answer_text=answer_text
            )
        
        messages.success(request, 'Thank you for completing the survey!')
        return redirect('surveys')
    
    context = {
        'survey': survey,
        'children': children,
        'households': households,
    }
    return render(request, 'children/survey_take.html', context)


def survey_results(request, pk):
    """Survey Results - View all responses (Admin and Volunteers)"""
    survey = get_object_or_404(Survey.objects.prefetch_related(
        'questions', 'responses__respondent', 'responses__answers'
    ), pk=pk)
    
    responses = survey.responses.all().order_by('-submitted_at')
    
    context = {
        'survey': survey,
        'responses': responses,
    }
    return render(request, 'children/survey_results.html', context)
