from django.shortcuts import render, redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib import auth
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from mainapp.models import *
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta, date
from django.views.decorators.csrf import csrf_exempt
from .forms import LeavesForm
from .utlis import *
from calendar import monthrange
from django.db.models import Count, Q
import pytz
import json
from django.conf import settings

# Create your views here.
def index(request):
    if check_allowed_ip(request):
        # User's IP address is allowed
        user = Profile.objects.all()
        context = {'user': user}
        return render(request, 'index.html', context)
    else:
        # User's IP address is not allowed
        return HttpResponse('Access Denied')

@login_required(login_url='login')
def home(request):
    user = request.user
    fullname = request.user.get_full_name()
    profile = Profile.objects.get(user=request.user)
    today = timezone.now().date()
    notices = Notice.objects.all()
    attendance = Attendance.objects.filter(user=user, dateOfQuestion=today).first()
    first_day, last_day = get_current_month_range()
    attendances=Attendance.objects.filter(user=user, dateOfQuestion__range=(first_day, last_day))
    present_count = attendances.filter(status='Present').count()
    late_count = attendances.filter(status='Late').count()
    absent_count = attendances.filter(status='Absent').count()
    
    if attendance:
        hours, minutes, seconds = attendance.calculate_duration_hms()
    else:
        hours, minutes, seconds = 00, 00, 00
    context = {
        'notices':notices,
        'fullname': fullname,
        'profile': profile,
        'navbar': 'home',
        'attendance': attendance,
        'hours': hours,
        'minutes': minutes,
        'seconds': seconds,
        'present_count':present_count,
        'late_count':late_count,
        'absent_count':absent_count,
        
    }
    return render(request, 'home.html', context)


#login request gets value from action of html.login/form
def login(request):
    
    if request.user.is_authenticated:
         return redirect ('home')
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)

        user = auth.authenticate(username= username, password= password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, "Credentials Invalid")
            return redirect ('login')
    else:
        return render(request,'login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')

def get_current_month_range():
    today = timezone.now().date()
    first_day = date(today.year, today.month, 1)
    last_day = date(today.year, today.month, 28)  # Assuming all months have 28 days
    while last_day.month == today.month:
        last_day = last_day + timedelta(days=1)
    last_day = last_day - timedelta(days=1)
    return first_day, last_day

@login_required
def information(request):
    user = request.user
    profile = Profile.objects.get(user=request.user)
    first_day, last_day = get_current_month_range()
    attendances = Attendance.objects.filter(user=user, dateOfQuestion__range=(first_day, last_day))
    late_count = attendances.filter(status='Late').count()
    department=profile.department
    department_schedules = Schedule.objects.filter(department=department)
    context={
        'late_count': late_count,
        'profile': profile,
        'navbar': 'yourinformation',
        'department_schedules': department_schedules,
    }
    print(late_count)
    return render(request, 'your_information.html', context)

@login_required(login_url='login')
def notice(request):
    user_object = User.objects.get(username=request.user.username)
    profile = Profile.objects.get(user=user_object)
    notices= Notice.objects.all()
    context={
        'profile':profile,
        'notices':notices,
        'navbar':'notice',
        
    }
    return render(request,'notices.html',context)

@login_required(login_url='login')
def attendance(request):
    user_object = User.objects.get(username=request.user.username)
    profile = Profile.objects.get(user=user_object)
    notices= Notice.objects.all()
    context={
        'profile':profile,
        'notices':notices,
        'navbar':'attendance',
        
    }
    return render(request,'attendance.html',context)
    
    
@csrf_exempt
def checkin(request):
    # if request.is_ajax():
    if request.method == 'POST':
        print("CHECK IN")
        user = request.user
        dateOfQuestion = timezone.now().date()
        checkInTime = timezone.now()
        print(checkInTime)
        Attendance.objects.create(user=user, checkInTime=checkInTime,dateOfQuestion=dateOfQuestion)
        return JsonResponse({'in_time': checkInTime})
    response = {'message': 'Success'}
    return JsonResponse(response)

@csrf_exempt
def checkout(request):
    if request.method == 'POST':
        print("CHECK OUT")
        user = request.user
        checkOutTime = timezone.now()
        attendance_date = datetime.now(timezone.utc).date()
        try:
            current_attendance = Attendance.objects.filter(user=user, dateOfQuestion=attendance_date).latest('checkInTime')
        except Attendance.DoesNotExist:
            return JsonResponse({'message': 'No check-in record found for today'})

        current_attendance.checkOutTime = checkOutTime
        current_attendance.duration = (checkOutTime - current_attendance.checkInTime).total_seconds() / 3600

        # Get the schedule of the user's department
        profile = Profile.objects.get(user=request.user)
        department = profile.department.id
        schedule = Schedule.objects.get(department=department)
        late_time = datetime.combine(date.today(), schedule.schedule_start) + timedelta(minutes=15)
        late_time = late_time.time()

        # Get the user's time zone from the session, or use a default time zone
        user_tz = pytz.timezone(request.session.get('django_timezone', settings.TIME_ZONE))

        # Localize the check-in and check-out times to the user's time zone
        check_in_time = current_attendance.checkInTime.astimezone(user_tz)
        check_out_time = checkOutTime.astimezone(user_tz)

        # Determine the status based on the schedule and check-in time
        if check_in_time.time() < late_time:
            current_attendance.status = 'Present'
        else:
            current_attendance.status = 'Late'

        current_attendance.save()

        return JsonResponse({'out_time': check_out_time.time().strftime('%H:%M:%S'), 'duration': current_attendance.duration})
    response = {'message': 'Success'}
    return JsonResponse(response)
        







#####################################LEAVES############################################
@login_required(login_url='login')
def leaves(request):
    leaves= Leaves.objects.filter(user_id=request.user.id)
    submitted=False
    profile=Profile.objects.get(user=request.user)
    form = LeavesForm()
    if request.method == 'POST':
        form = LeavesForm(request.POST)
        if form.is_valid():
            form.instance.user_id = request.user.id
            # Leaves = form.save(commit=False)
            # Leaves.user = request.user
            form.save()
            return HttpResponseRedirect('leaves?submitted=True')
    else:
        form=LeavesForm()
        if 'submitted in request.GET':
            submitted=True
    context={
        'profile':profile,
        'navbar':'leaves',
        'form': form,
        'submitted':submitted,
        'leaves':leaves,
            }
    return render(request,'leaves.html',context)

@login_required(login_url='login')
def payroll(request):
    user_object = User.objects.get(username=request.user.username)
    try:
        payrolls = Payroll.objects.filter(user=user_object)
        net_salary = None # Define net_salary before the loop
        for payroll in payrolls:
            net_salary = payroll.calculate_net_pay()
            payroll.net_pay = net_salary
            payroll.save()
    except IndexError:
        print("No payroll object found for this user")
        payrolls = None
    else:
        print("Payroll object found:", payrolls)
    profile = Profile.objects.get(user=user_object)
    context={
        'profile':profile,
        'navbar':'Salary',
        'payrolls': payrolls,
        'net_salary': net_salary,
    }
    return render(request,'Salary_Sheet.html', context)


def view_pdf(request, pk):
    user_object = User.objects.get(username=request.user.username)
    payroll = Payroll.objects.filter(user=user_object, id=pk)[0]
    profile = Profile.objects.get(user=user_object)
    user = request.user
    fullname = request.user.get_full_name()
    data = {
            'fullname':fullname,
            'payroll': payroll,
            'user': user_object,
            'profile': profile,
            }
    print(data)
    pdf = render_to_pdf('payroll_pdf.html', data)
    return HttpResponse(pdf, content_type='application/pdf')

def download_pdf(request, pk):
    user_object = User.objects.get(username=request.user.username)
    user = request.user
    fullname = request.user.get_full_name()
    payroll = Payroll.objects.filter(user=user_object, id=pk)[0]
    profile = Profile.objects.get(user=user_object)
    data = {
            'fullname':fullname,
            'payroll': payroll,
            'user': user_object,
            'profile': profile,
            }
    print(data)	
    pdf = render_to_pdf('payroll_pdf.html', data)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="payroll.pdf"'
    return response



import calendar

def chart(request, year, month):
    user_object = User.objects.get(username=request.user.username)
    profile=Profile.objects.get(user=user_object)
    # Convert year and month to a timezone-aware datetime object
    start_date = timezone.datetime(int(year), int(month), 1, tzinfo=timezone.get_current_timezone()).date()
    
    # Find the number of days in the specified month
    _, num_days = monthrange(start_date.year, start_date.month)
    
    # Calculate the end date as the last day of the specified month
    end_date = timezone.datetime(int(year), int(month), num_days, 23, 59, 59, tzinfo=timezone.get_current_timezone()).date()

    # Query the database to get the counts for each status for the specified user and month
    status_counts = Attendance.objects.filter(Q(user=user_object) & Q(dateOfQuestion__range=(start_date, end_date))).values('status').annotate(count=Count('status'))

    # Calculate the score
    total_present = 0
    total_late = 0
    total_absent = 0
    for status in status_counts:
        if status['status'] == 'Present':
            total_present = status['count']
        elif status['status'] == 'Late':
            total_late = status['count']
        elif status['status'] == 'Absent':
            total_absent = status['count']
    total_score = total_present * 10 + total_late * 8 + total_absent * (-5)
    total_days = total_present + total_late + total_absent
    if total_days == 0:
        average_score = 0
    else:
        average_score = total_score / total_days
    
    # Create a list of labels and values for the pie chart
    labels = [status['status'] for status in status_counts]
    values = [status['count'] for status in status_counts]
    
    # Get the month name from the month number
    month_name = calendar.month_name[int(month)]

    # Pass the labels, values, month name, and average score to the template context
    context = {'labels': labels,
               'values': values,
               'month_name': month_name,
               'average_score': average_score,
               'profile':profile,
               'navbar': 'chart'}
    print(average_score)

    return render(request, 'chart.html', context)



def generate_chart(request):
    today = date.today()
    year = today.year
    month = today.month
    print(year,month)
    # context = {
    #     'profile': profile,
    #     'year':year,
    #     'month':month,
        
    #     }
    if request.method == 'GET':
        year = request.GET.get('year',year)
        month = request.GET.get('month',month)
        # if year and month:
        #     context['year'] = year
        #     context['month'] = month
        return redirect('chart', int(year), int(month))
    return redirect('chart',int(year),int(month))


