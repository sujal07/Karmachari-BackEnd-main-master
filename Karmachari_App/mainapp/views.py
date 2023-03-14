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
import pytz
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

@login_required(login_url='login')
def information(request):
      profile=Profile.objects.get(user=request.user)
      context={
      'profile':profile,
      'navbar':'yourinformation',
      
    }
      return render(request,'your_information.html',context)

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
        dateOfQuestion = datetime.today()
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
        current_attendance = Attendance.objects.filter(user=user).latest('checkInTime')
        current_attendance.checkOutTime = checkOutTime
        current_attendance.save()
        duration = current_attendance.calculate_duration()

        # Get the schedule of the user's department
        profile = Profile.objects.get(user=request.user)
        department = profile.department.id
        schedule = Schedule.objects.get(department=department)
        late_time = datetime.combine(date.today(), schedule.schedule_start) + timedelta(minutes=15)
        late_time = late_time.time()
        attendance_date = date.today()

        # Get the user's time zone from the session, or use a default time zone
        user_tz = pytz.timezone(request.session.get('django_timezone', settings.TIME_ZONE))

        # Get the user's schedule start time in the user's time zone
        schedule_start = user_tz.localize(datetime.combine(attendance_date, schedule.schedule_start))

        # Localize the check-in time to the user's time zone
        check_in_time = current_attendance.checkInTime.astimezone(user_tz)

        # Determine the status based on the schedule and check-in time
        check_in_time = current_attendance.checkInTime.astimezone(timezone.get_current_timezone()).time()
        if check_in_time < late_time:
            status = 'Present'
        else:
            status = 'Late'

        # Get the attendance object for the user and the current date
        attendance_date = datetime.now(timezone.utc).date()
        try:
            attendance = Attendance.objects.filter(user=user, dateOfQuestion=attendance_date).latest('checkInTime')
        except Attendance.DoesNotExist:
            attendance = None

        print('checkOutTime:', current_attendance.checkOutTime)
        print('late_time:', late_time)
        print('status:', status)
        print(check_in_time)

        # If an attendance object already exists, update its checkOutTime, duration, and status
        if attendance is not None:
            attendance.checkOutTime = checkOutTime
            attendance.duration = duration
            attendance.status = status
            attendance.save()
            print(attendance.checkOutTime)
        else:
            # Create a new attendance object
            attendance = Attendance.objects.create(
                user=user,
                name=profile.user.get_full_name(),
                duration=duration,
                status=status,
                dateOfQuestion=attendance_date,
                checkOutTime=checkOutTime,
            )

    return JsonResponse({'out_time': checkOutTime, 'duration': duration})
        







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
        'navbar':'Salary-Sheet',
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