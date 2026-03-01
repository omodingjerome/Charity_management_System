"""
Passenger WSGI config for DreamHost
"""
import os
import sys

# Add project to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'charity_system.settings')

# For production, set DEBUG=False
os.environ['DEBUG'] = 'False'
os.environ['ALLOWED_HOSTS'] = 'cms.reachapac.org,www.cms.reachapac.org'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
