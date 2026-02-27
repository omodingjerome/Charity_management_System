"""
URL Configuration for HTML Frontend
"""
from django.urls import path
from . import views_html

# Note: No app_name to avoid namespace conflict with API URLs

urlpatterns = [
    path('login/', views_html.login_view, name='login'),
    path('signup/', views_html.signup_view, name='signup'),
    path('logout/', views_html.logout_view, name='logout'),
    path('', views_html.home, name='home'),
    path('children/', views_html.children_directory, name='children-directory'),
    path('children/<int:pk>/', views_html.child_detail, name='child-detail'),
    path('children/add/', views_html.add_child, name='add-child'),
    path('households/', views_html.households_list, name='households'),
    path('households/add/', views_html.add_household, name='add-household'),
    path('volunteers/', views_html.volunteers_list, name='volunteers'),
    path('volunteers/add/', views_html.add_volunteer, name='add-volunteer'),
    
    # Survey URLs
    path('surveys/', views_html.surveys_list, name='surveys'),
    path('surveys/create/', views_html.survey_create, name='survey-create'),
    path('surveys/<int:pk>/', views_html.survey_detail, name='survey-detail'),
    path('surveys/<int:pk>/take/', views_html.survey_take, name='survey-take'),
    path('surveys/<int:pk>/results/', views_html.survey_results, name='survey-results'),
]
