"""
Django Signals for Child model - Auto ID generation
"""
from django.db.models.signals import pre_save
from django.dispatch import receiver
from children.models import Child


@receiver(pre_save, sender=Child)
def generate_child_id(sender, instance, **kwargs):
    """
    Automatically generate a unique child_id if not provided.
    Format: CHILD-YYYYMMDD-XXXX where XXXX is a sequential number
    """
    if not instance.child_id:
        # Get the current year-month-day
        from datetime import datetime
        today = datetime.now().strftime('%Y%m%d')
        
        # Get the count of existing children to generate sequential number
        count = Child.objects.count() + 1
        
        # Format: CHILD-20240304-0001
        instance.child_id = f'CHILD-{today}-{count:04d}'
