from django.db import models
from datetime import date

# Create your models here.


from django.core.validators import MinLengthValidator

class Contact(models.Model):
    id = models.AutoField(primary_key=True)
    plot = models.ForeignKey('Plot', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField()

    def __str__(self):
        return f"{self.name} - {self.plot}"

class User(models.Model):
    id = models.AutoField(primary_key=True)
    is_admin = models.BooleanField(default = False)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    otp = models.CharField(max_length=6, blank=True, null=True)
    messages = models.ManyToManyField(Contact, blank=True, related_name='user_messages')
    phone = models.BigIntegerField(validators=[MinLengthValidator(limit_value=15)])
    password = models.CharField(max_length=120)
    is_subscribed = models.BooleanField(default=False)
    sub_start = models.DateField(default=date.today)  # Example format: YYYY-MM-DD
    sub_end = models.DateField(default=date.today) 
    # sub_start = models.DateField()  # Example format: YYYY-MM-DD
    # sub_end = models.DateField()  
    
    def __str__(self):
        # Format sub_start and sub_end dates as 'dd-mm-yyyy'
        formatted_sub_start = self.sub_start.strftime('%d-%m-%Y')
        formatted_sub_end = self.sub_end.strftime('%d-%m-%Y')
        return f'{self.name} (Sub Start: {formatted_sub_start}, Sub End: {formatted_sub_end})'

class Conus(models.Model):
    id = models.AutoField(primary_key=True)
    name =  models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    phone = models.BigIntegerField(validators=[MinLengthValidator(limit_value=10)])
    message = models.TextField()


class Plot(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey('v0.User', on_delete=models.SET_NULL, related_name='owned_plots', null=True, default=None)
    is_sub_user = models.BooleanField(default=False)
    pimg = models.ImageField(upload_to='media/')
    pcity = models.CharField(max_length=255)
    pstate = models.CharField(max_length=80)
    paddress_line = models.CharField(max_length=1000)
    plandmark = models.CharField(max_length=255)
    area = models.IntegerField(null=True)
    sprice = models.BigIntegerField(null = True)
    price = models.IntegerField(null=True)
    is_rent = models.BooleanField(default=False)
    is_south = models.BooleanField(default=False)
    is_north = models.BooleanField(default=False)
    is_east = models.BooleanField(default=False)
    is_south_east = models.BooleanField(default=False)
    is_north_east = models.BooleanField(default=False)
    is_1 = models.BooleanField(default=False)
    is_2 = models.BooleanField(default=False)
    is_3 = models.BooleanField(default=False)
    has_boundary_wall = models.BooleanField(default=False)
    is_corner_plot = models.BooleanField(default=False)
    is_gated_property = models.BooleanField(default=False)
    fname = models.CharField(max_length=255)
    lname = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    smsg = models.TextField()

    def __str__(self):
        return f"{self.pcity} - {self.plandmark}"

    
class UserPlot(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('v0.User', on_delete=models.CASCADE)
    plot = models.ForeignKey('v0.Plot', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} - {self.plot}"