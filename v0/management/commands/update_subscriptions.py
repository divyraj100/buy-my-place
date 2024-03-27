from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from v0.models import User  # Import your User model

class Command(BaseCommand):
    help = 'Updates subscription statuses of users'

    def handle(self, *args, **kwargs):
        current_date = timezone.now().date() 
        expired_users = User.objects.filter(sub_end__lte=current_date, is_subscribed=True)
        
        for user in expired_users:
            if user.sub_end is not None:
                if user.sub_end < current_date:
                    # Subscription has expired, deactivate it
                    user.is_subscribed = False
                  
            elif not user.sub_start:
                # Activate subscription
                user.sub_start = current_date
                # Calculate subscription end date (e.g., 30 days from start date)
                user.sub_end = current_date + timedelta(days=30)
                
            user.save()
        
        self.stdout.write(self.style.SUCCESS('Subscription statuses updated successfully'))
