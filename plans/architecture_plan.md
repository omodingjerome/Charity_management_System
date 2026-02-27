# Charity Management System - Architecture Plan

## Project Overview
- **Tech Stack**: Django 4+, Django REST Framework, PostgreSQL, JWT Authentication
- **Project Type**: Child Scholarship Program Management System

## Application Structure
```
charity_system/
├── charity_system/          # Main Django project
│   ├── settings.py          # Django settings
│   ├── urls.py              # Root URL configuration
│   └── wsgi.py
├── children/                # Child management app
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── households/              # Household management app
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── admin.py
├── schools/                 # Schools app
├── projects/               # Projects/Events app
└── requirements.txt
```

## Data Model Diagram

```mermaid
erDiagram
    Child ||--o{ Caregiver : "has"
    Child ||--o| Household : "belongs_to"
    Child ||--o{ Project : "enrolled_in"
    Child ||--o| School : "attends"
    Household ||--o{ Caregiver : "has"
    
    Child {
        string name
        date date_of_birth
        int age PK
        image profile_photo
        string child_id UK
        string chronic_condition
        string income_provider
        string education_payer
        string medical_payer
        bool caregiver_disability
        bool emergency_expense
        string household_assets
        int household_size
        string income_source
        bool consistent_income
        int children_under_18
        bool savings_group
        string residence_type
        decimal monthly_income
    }
    
    Household {
        string household_name PK
        int number_of_people
        string main_income_source
        bool consistent_income_6months
        int children_under_18
        bool savings_group
        string residence_type
        decimal estimated_monthly_income
    }
    
    Caregiver {
        string name
        string relationship
        string phone
        string email
        bool has_disability
    }
    
    School {
        string name PK
        string location
        string level
    }
    
    Project {
        string name PK
        date start_date
        date end_date
        string description
    }
```

## Key Design Decisions

1. **Age Calculation**: Auto-calculated from date_of_birth using a property/method
2. **Unique Child ID**: Enforced at model level with unique=True
3. **Photo Uploads**: Using Django's ImageField with secure file handling
4. **Relationships**: 
   - Child → Household (ForeignKey - one-to-many)
   - Child → Caregiver (ForeignKey - one-to-many)
   - Child → School (ForeignKey - many-to-one)
   - Child → Project (ManyToMany)
5. **Indexes**: On child_id, date_of_birth, and frequently queried fields
