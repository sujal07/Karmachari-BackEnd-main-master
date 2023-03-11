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
    fullname =  request.user.get_full_name()
    profile=Profile.objects.get(user=request.user)
    context = {'fullname':fullname,
               'profile':profile,
               'navbar':'home',
               }
    return render(request,'Home.html',context)


    
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
        Attendance.objects.create(user=user, checkInTime=checkInTime,dateOfQuestion=dateOfQuestion)
        return JsonResponse({'in_time': checkInTime})
    response = {'message': 'Success'}
    return JsonResponse(response)

@csrf_exempt
def checkout(request):
    # if request.is_ajax():
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


        # Determine the status based on the schedule and check-in time
        if current_attendance.checkInTime.time() > late_time:
            status = 'Late'  # Late
        else:
            status = 'Present'  # Presents
    try:
        attendance = Attendance.objects.filter(user=user, dateOfQuestion=attendance_date).latest('checkInTime')
    except Attendance.DoesNotExist:
        attendance = None

    # If an attendance object already exists, update its checkOutTime, duration, and status
    if attendance is not None:
        attendance.checkOutTime = checkOutTime
        attendance.duration = duration
        attendance.status = status
        attendance.save()
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
            # 'navbar':'leaves',
            'form': form,
            'submitted':submitted,
            'leaves':leaves,
            }
            return render(request,'leaves.html',context)

@login_required(login_url='login')
def salary(request):
    user_object = User.objects.get(username=request.user.username)
    profile = Profile.objects.get(user=user_object)
    context={
        'profile':profile,
        'navbar':'salary',
        
    }
    return render(request,'Salary_Sheet.html',context)


# def mark_absent():
#         # Get all users
#         users = User.objects.all()
#         # Get today's date
#         today = timezone.now().date()
#         # Loop through each user
#         for user in users:
#             # Check if the user has a check-in/out record for today
#             attendance_exists = Attendance.objects.filter(user=user, dateOfQuestion=today).exists()
#             if not attendance_exists:
#                 # If no attendance record exists, create a new one with a status of 'Absent'
#                 attendance = Attendance(user=user, dateOfQuestion=today, status='Absent')
#                 attendance.save()
                
# def mark_saturdays_as_leave(year, month):
#     user=User.objects.all()
#     # Get the first and last day of the month
#     first_day = date(year, month, 1)
#     last_day = date(year, month, 28) + timedelta(days=4)

#     # Loop through each Saturday in the month and mark it as Leave
#     d = first_day
#     while d <= last_day:
#         if d.weekday() == 5:
#             Attendance.objects.update_or_create(
#                 user=user,
#                 dateOfQuestion=d,
#                 defaults={
#                     'status': 'Leave'
#                 }
#             )
#         d += timedelta(days=1)