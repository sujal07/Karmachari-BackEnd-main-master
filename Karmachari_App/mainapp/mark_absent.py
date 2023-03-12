from django.core.management.base import BaseCommand
from django.utils import timezone
from mainapp.views import mark_saturdays_as_leave,mark_absent
from mainapp.models import Attendance, User
import schedule


class Command(BaseCommand):
    help = 'Marks users as absent if they did not check in/out'

    def handle(self, *args, **options):
        
        def mark_absent():
            # Get all users
            users = User.objects.all()
            # Get today's date
            today = timezone.now().date()
            # Loop through each user
            for user in users:
                # Check if the user has a check-in/out record for today
                attendance_exists = Attendance.objects.filter(user=user, dateOfQuestion=today).exists()
                if not attendance_exists:
                    # If no attendance record exists, create a new one with a status of 'Absent'
                    attendance = Attendance(user=user, dateOfQuestion=today, status='Absent')
                    attendance.save()
                    
    def mark_saturdays_as_leave(year, month):
            from calendar import monthrange
            _, num_days = monthrange(year, month)
            for day in range(1, num_days + 1):
                date = timezone.datetime(year, month, day).date()
                if date.weekday() == 5:  # Saturday is the 5th day of the week
                    for user in User.objects.all():
                        attendance, _ = Attendance.objects.get_or_create(user=user, dateOfQuestion=date)
                        attendance.status = 'Leave'
                        attendance.save()
                        
    schedule.every().month.do(lambda: mark_saturdays_as_leave(timezone.now().year, timezone.now().month))

        # Schedule the function to run at the end of the day
    schedule.every().day.at('23:59').do(mark_absent)

        # Run the schedule loop
    while True:
        schedule.run_pending()
