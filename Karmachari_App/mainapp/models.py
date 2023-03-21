from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse
from django.utils.html import mark_safe

User=get_user_model()

class Salary(models.Model):
    post = models.CharField(max_length=100, null=True)
    hourly_rate = models.FloatField(null=True)
    def __str__(self):
        return self.post
    
class Department(models.Model):
    name = models.CharField(max_length=100, default="Everyone", null=True)
    # Post = models.CharField(max_length=100, null=True)
    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    userID = uuid.uuid4()
    profileimg = models.ImageField(upload_to='profile_images',default='img.png')
    dob = models.DateField()
    post=models.ForeignKey(Salary, on_delete=models.CASCADE,null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=100, default=0)
    def __str__(self):
        return self.user.username
    
    def img_preview(self): #new
        return mark_safe(f'<img src = "{self.profileimg.url}" width = "300"/>')
    
class Notice(models.Model):
    title = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(default=datetime.now)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    context = models.TextField(max_length=100000, null=True)        
    def __str__(self):
        return self.title

class Leaves(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    leave_condn = (
        ('Sick Leave','Sick Leave'),
        ('Vacation','Vacation'),
        ('Emergency','Emergency')
    )
    leave_permission = (
        ('Approved','Approved'),
        ('Pending','Pending'),
        ('Not Approved','Not Approved')
    )
    subject = models.CharField(max_length=100, null=True)
    date = models.DateField(default=timezone.now)
    duration = models.DateField(default=timezone.now)
    leave_type = models.CharField(max_length=100, null=True,choices= leave_condn)
    message = models.TextField(max_length=100000, null=True)
    status = models.CharField(max_length=100, choices= leave_permission, default='Pending')
    def __str__(self):
        return self.subject
    
    
class Schedule(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    schedule_start = models.TimeField()
    schedule_end = models.TimeField()
    def __str__(self):
        return self.department.name
    
    
class Payroll(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    basic_pay = models.DecimalField(max_digits=8, default=10000, decimal_places=2)
    bonus = models.DecimalField(max_digits=8,null=True, decimal_places=2)
    deductions = models.DecimalField(max_digits=8,null=True, decimal_places=2)
    net_pay = models.DecimalField(max_digits=8,default= 0, blank=True, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    
    def calculate_net_pay(self):
        net_pay =self.basic_pay + self.bonus - self.deductions
        return(net_pay)
    
    def salary_preview(self):
        return (self.net_pay)
    
    def hour_worked_preview(self):
        return (self.hours_worked)
    
    def __str__(self):
        return f"{self.user.username}'s Payroll for {self.date.strftime('%Y-%m-%d')}"
    
    
class AllowedIP(models.Model):
    ip_address = models.GenericIPAddressField(null=True)
    # def __str__(self):
    #     return self.
    
class Attendance(models.Model):
    STATUS_CHOICES = (
        ('Late', 'Late'),
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Leave', 'Leave'),
        ('Holiday','Holiday')
    )
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    dateOfQuestion = models.DateField(null=True)
    checkInTime = models.DateTimeField(null=True)
    checkOutTime = models.DateTimeField(null=True)
    # overtime = models.DateTimeField(null=True,blank=True)
    name=models.CharField(max_length=255,null=True)
    duration = models.FloatField(null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        self.name = f"{self.user.first_name} {self.user.last_name}"
        super().save(*args, **kwargs)
        
    def calculate_duration(self):
        if self.checkOutTime:
            duration = self.checkOutTime - self.checkInTime
            return duration.total_seconds() / 3600.0 # Convert to hours
        else:
            return 0
        
    def calculate_duration_hms(self):
        if self.checkOutTime:
            duration = self.checkOutTime - self.checkInTime
            seconds = int(duration.total_seconds())
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            return hours, minutes, seconds
        else:
            return 0, 0, 0

class Events(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    id = models.AutoField(primary_key=True)
    event_status= models.CharField(max_length=255,null=True)
    start = models.DateTimeField(null=True,blank=True)
    end = models.DateTimeField(null=True,blank=True)
 
    class Meta:  
        db_table = "tblevents"
        
class Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    device_id = models.CharField(max_length=1000)
    
    def set_device_id(self, device_id):
        self.device_id = device_id
        self.save()
    
    def __str__(self):
        return self.user.username


        
        