import calendar
from datetime import date, datetime, time, timedelta
from django.utils.timezone import make_aware
from mainapp.models import Attendance, User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Marks all Saturdays in a given month as Leave for all users'
    
    def add_arguments(self, parser):
        parser.add_argument('year', type=int, help='The year for which to mark Saturdays as Leave')
        parser.add_argument('month', type=int, help='The month for which to mark Saturdays as Leave')
    
    def handle(self, *args, **options):
        year = options['year']
        month = options['month']
        
        # Get the first and last day of the month
        first_day = date(year, month, 1)
        last_day = date(year, month, calendar.monthrange(year, month)[1])
        today = datetime.now().date()

        # Loop through each Saturday in the month and mark it as Leave
        for day in range(1, last_day.day + 1):
            loop_date = datetime(year, month, day).date()

            if loop_date.weekday() == 5:  # Saturday is the 5th day of the week
                for user in User.objects.all():
                    next_saturday = loop_date + timedelta((7-today.weekday()) % 4)
                    attendance, _ = Attendance.objects.get_or_create(user=user, dateOfQuestion=next_saturday)
                    attendance.status = 'Leave'
                    attendance.checkInTime = make_aware(datetime.combine(next_saturday, time(0, 0)))
                    attendance.checkOutTime = make_aware(datetime.combine(next_saturday, time(0, 0)))
                    attendance.save()
                    self.stdout.write(self.style.SUCCESS(f'Saturday marked as Leave for {user.username}'))

