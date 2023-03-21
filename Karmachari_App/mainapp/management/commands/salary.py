from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from mainapp.models import Attendance, Payroll,Salary,Profile
from django.contrib.auth.models import User
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Generates payroll for all users for a given month'

    def add_arguments(self, parser):
        parser.add_argument('month', type=int, help='Month for which payroll is to be generated')
        parser.add_argument('year', type=int, help='Year for which payroll is to be generated')

    def handle(self, *args, **kwargs):
        month = kwargs['month']
        year = kwargs['year']
        users = User.objects.all()

        for user in users:
            profile=Profile.objects.get(user=user)
            salary=profile.post
            hourly_rate=salary.hourly_rate
            attendance = Attendance.objects.filter(user=user, dateOfQuestion__year=year, dateOfQuestion__month=month)

            if attendance:
                total_hours_worked = sum(a.duration for a in attendance if a.duration is not None)
            else:
                total_hours_worked = 0

            late_count = attendance.filter(status='Late').count()
            basic_pay = total_hours_worked *hourly_rate
            bonus = basic_pay * 0.1
            deductions = late_count * 25
            net_pay = basic_pay + bonus - deductions

            payroll = Payroll.objects.create(
                user=user,
                basic_pay=basic_pay,
                bonus=bonus,
                deductions=deductions,
                net_pay=net_pay,
                date=timezone.now(),
            )

            print(f"Payroll generated for {user.username} for {month}/{year}: Basic Pay: {basic_pay}, Bonus: {bonus}, Deductions: {deductions}, Net Pay: {net_pay}")
