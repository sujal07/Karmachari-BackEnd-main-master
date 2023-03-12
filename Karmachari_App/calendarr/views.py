from django.shortcuts import render
from django.http import JsonResponse 
from mainapp.models import Events,Profile
from mainapp.models import Attendance
import json
 
# Create your views here.
# def calendar(request):  
#     user = request.user
#     all_events = Events.objects.filter(user=user)
#     profile=Profile.objects.get(user=request.user)
#     events = []
#     for event in all_events:
#         events.append({
#             'title': event.event_status,                                                                                         
#             'id': event.id,                                                                                              
#             'start': event.start.strftime("%m/%d/%Y, %H:%M:%S"),                                                         
#             'end': event.end.strftime("%m/%d/%Y, %H:%M:%S"),
#         })
    
#     context = {
#         'events': json.dumps(events),
#         'profile':profile,
#         'navbar':'attendance',
#     }
#     return render(request, 'calendar.html', context)

def calendar(request):  
    user = request.user
    all_events = Events.objects.filter(user=user)
    profile=Profile.objects.get(user=request.user)
    events = []
    for event in all_events:
        events.append({
            'title': event.event_status,                                                                                         
            'id': event.id,                                                                                              
            'start': event.start.strftime("%m/%d/%Y, %H:%M:%S"),                                                         
            'end': event.end.strftime("%m/%d/%Y, %H:%M:%S"),
        })
    all_attendance = Attendance.objects.filter(user=user)
    for attendance in all_attendance:
        events.append({
            'title': attendance.status,                                                                                         
            'id': attendance.id,                                                                                              
            'start': attendance.checkInTime.strftime("%m/%d/%Y, %H:%M:%S"),                                                         
            'end': attendance.checkOutTime.strftime("%m/%d/%Y, %H:%M:%S"),
            'className': 'attendance',
        })
    
    context = {
        'events': json.dumps(events),
        'profile':profile,
        'navbar':'attendance',
    }
    return render(request, 'calendar.html', context)
