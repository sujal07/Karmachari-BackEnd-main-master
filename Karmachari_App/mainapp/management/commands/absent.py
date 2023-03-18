import random
from datetime import datetime
from django.core.management.base import BaseCommand
from mainapp.models import Attendance, User
from calendar import monthrange
from datetime import date, datetime, time, timedelta
from django.utils.timezone import make_aware

class Command(BaseCommand):
    help = 'Generates random check-in and check-out data'

    def add_arguments(self, parser):
        parser.add_argument('year', type=int, help='Year number (e.g. 2023)')
        parser.add_argument('month', type=int, help='Month number (1-12)')

    def handle(self, *args, **options):
        month = options['month']
        year = options['year']

        users = User.objects.all()
        for user in users:
            num_days = monthrange(year, month)[1]
            absent_dates = random.sample(range(1, num_days+1), random.randint(0, 2))

        
            for day in range(1, num_days+1):
                date_of_question = datetime(year=year, month=month, day=day)

                if day in absent_dates:
                    if not Attendance.objects.filter(user=user, dateOfQuestion=date_of_question).exists():
                        Attendance.objects.create(
                                                user=user, 
                                                status='Absent',
                                                dateOfQuestion=date_of_question,
                                                checkInTime=make_aware(datetime.combine(date_of_question, datetime.min.time())), 
                                                checkOutTime=make_aware(datetime.combine(date_of_question, datetime.min.time())))
                        self.stdout.write(self.style.SUCCESS(f'Successfully generated attendance data for user {user.id} on {date_of_question.date()}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Skipping generation of attendance data for user {user.id} on {date_of_question.date()}'))
