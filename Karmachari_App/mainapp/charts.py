from mainapp.models import Attendance
from django.db.models import Count
from django.utils import timezone

def attendance_chart_data():
    labels = []
    present_data = []
    absent_data = []
    leave_data = []

    # Get the last 7 days
    today = timezone.now().date()
    last_week = today - timezone.timedelta(days=7)

    # Loop through the last 7 days and get the attendance data
    for i in range(7):
        date = last_week + timezone.timedelta(days=i)
        labels.append(date.strftime('%m/%d'))

        present_count = Attendance.objects.filter(dateOfQuestion=date, status='Present').count()
        present_data.append(present_count)

        absent_count = Attendance.objects.filter(dateOfQuestion=date, status='Absent').count()
        absent_data.append(absent_count)

        leave_count = Attendance.objects.filter(dateOfQuestion=date, status='Leave').count()
        leave_data.append(leave_count)

    return {
        'labels': labels,
        'datasets': [
            {
                'label': 'Present',
                'data': present_data,
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 1
            },
            {
                'label': 'Absent',
                'data': absent_data,
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderWidth': 1
            },
            {
                'label': 'Leave',
                'data': leave_data,
                'backgroundColor': 'rgba(255, 206, 86, 0.2)',
                'borderColor': 'rgba(255, 206, 86, 1)',
                'borderWidth': 1
            }
        ]
    }
