from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from .models import *
import os
import random
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from twilio.rest import Client
from django.core.mail import send_mail
from django.db.models import Q
from django.core.management import call_command



    
def generate_otp():
    return str(random.randint(100000, 999999))

def verify_otp_sms(phone_number, entered_otp):
    account_sid = "ACaf8f02ccd51e63331a684db76cd27755"
    auth_token = "f6d8c19cd83ef3415dbe6012d8de3086"
    verify_sid = "VA10ca81cd26491da2460ccd1d8f059b92"

    client = Client(account_sid, auth_token)

    try:
        verification_check = client.verify.v2.services(verify_sid) \
            .verification_checks \
            .create(to=phone_number, code=entered_otp)
        return verification_check.status
    except Exception as e:
        # Handle any exceptions that may occur during the verification check
        print(f"Error during OTP verification: {e}")
        return None


def send_otp_sms(phone_number):
    account_sid = "ACaf8f02ccd51e63331a684db76cd27755"
    auth_token = "f6d8c19cd83ef3415dbe6012d8de3086"
    verify_sid = "VA10ca81cd26491da2460ccd1d8f059b92"
    
    client = Client(account_sid, auth_token)

    verification = client.verify.v2.services(verify_sid) \
      .verifications \
      .create(to=phone_number, channel="sms")
    print(verification.status)

def send_otp_email(email, otp):
    subject = 'OTP Verification'
    message = f'Your OTP for registration is: {otp}'
    from_email = 'gidadivyraj10@gmail.com'
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list)

def Login_sign(request):
    if request.method == 'POST':
     
        full_name = request.POST.get('fname')
        email = request.POST.get('r-mail')
        phone = request.POST.get('r-phone')
        password = request.POST.get('r-cpass')
        request.session['registration_email'] = email
        request.session['registration_phone'] = phone


        if User.objects.filter(email=email).exists():
            cus_msg = '~ email is already registered'
            return render(request,'login_sign.html',{'cus_msg': cus_msg})  
        
        hashed_password = make_password(password)

        user = User(name=full_name, email=email, phone=phone, password=hashed_password, is_subscribed=False)
        user.save()

        email_otp = generate_otp()
        phone_otp = generate_otp()

        # Use transaction to ensure both OTPs are generated before sending
        with transaction.atomic():
            request.session['email_otp'] = email_otp
            request.session['phone_otp'] = phone_otp

            # Send OTPs to user's email and phone
            send_otp_email(email, email_otp)
            send_otp_sms(phone)

        return redirect('otp')
    return render(request, "login_sign.html")

def Login(request):
    if request.method == 'POST':
        umail = request.POST.get('u-mail') 
        password = request.POST.get('u-cpass')
        hashed_password = make_password(password)

        # user = User.objects.filter(name=username, password=hashed_password).first()

        if not umail or not password:
            cus_msg = '~ Incomplete Form '
            return render(request, "login.html", {'cus_msg': cus_msg})

        try:
            user = User.objects.get(email=umail)
        except User.DoesNotExist:
            cus_msg = '~ No user found'
            return render(request, "login.html", {'cus_msg': cus_msg})

        if not check_password(password, user.password):
            cus_msg = '~ Invalid Password'
            return render(request, "login.html", {'cus_msg': cus_msg})
        else:
            request.session['is_authenticated'] = True
            request.session['user_id'] = user.id
            request.session['is_admin'] = user.is_admin
            request.session['is_subscribed'] = user.is_subscribed
            cus_msg = 'Login successful'
            return redirect('Home_page')
    return render(request, "Login.html")


def landing_page(request):
    is_log = request.session.get('is_authenticated')
    
    if is_log:
        return redirect('Home_page')
    else:
        return render(request,'index.html')

def Home_page(request):

    latest_plots = Plot.objects.order_by('-id')[:3]  

    context = {
        'latest_plots': latest_plots,
    }
    return render(request, "home.html", context)


def forget(request):
    cus_msg=''

    if request.method == "POST":
        email = request.POST.get('email')
        request.session['forget_mail'] = email  # Storing email in session
        mail = request.session.get('forget_mail')  # Retrieving email from session

        try:
            user = User.objects.get(email=email)

            if email and user:
                otp = generate_otp()
                request.session['femail_otp'] = otp  # Storing OTP in session

                with transaction.atomic():
                    # Send OTP to user's email
                    send_otp_email(email, otp)

                return redirect('otp')  # Redirect to OTP verification page
            else:
                cus_msg = "Email is not registered"
        except ObjectDoesNotExist:
            cus_msg = "Email is not registered"

    return render(request, "forget.html",{'cus_msg':cus_msg})
    
def for_reset(request):

    if request.method == "POST":

        npass = request.POST.get('pass')
        rpass = request.POST.get('rpass')
        # hashed_passwordn = make_password(npass)
        # hashed_passwordr = make_password(rpass)

        umail = request.session.get('forget_mail')
        user = User.objects.get(email=umail)
        print(umail)

        if npass == rpass:

            hashed_passwordn = make_password(npass)
            
            if user:
                user.password = hashed_passwordn
                user.save()
                del request.session['forget_mail']


                return redirect('Login')
            else:
                cus_msg="email is not registered "
                return render(request, "for_reset.html", {"cus_msg": cus_msg})
        
        else:
            cus_msg="new and confirm passwords not matching"
            return render(request, "for_reset.html", {"cus_msg": cus_msg})

    return render(request, "for_reset.html")

def otp(request):
    cus_msg = ""
    email = request.session.get('registration_email')
    for_email = request.session.get('forget_mail')
    fotp = request.session.get('femail_otp')
    stored_email_otp = request.session.get('email_otp', None)
    stored_phone_otp = request.session.get('phone_otp', None)
    print(stored_email_otp)
    print(stored_phone_otp)


    if request.method == 'POST':
        entered_otp = request.POST.get('otp')

        phone_number = request.session.get('registration_phone', None)

            # Verify OTP for both email and phone
        phone_verification_status = verify_otp_sms(phone_number, entered_otp)

        if entered_otp == stored_email_otp or phone_verification_status == 'approved':
                # Clear the OTP and registration-related session variables after successful verification
            del request.session['email_otp']
            del request.session['phone_otp']
            del request.session['registration_email']
            del request.session['registration_phone']

            messages.success(request, 'OTP verified. You are now logged in.')
            return redirect('Login')  # Adjust this to your actual login URL
        elif entered_otp == fotp:
            
            # del request.session['forget_mail']
            return redirect('for_reset') 

        else:
            cus_msg = "~ Invalid OTP or User"


    return render(request, "otp.html", {'email': email, 'cus_msg': cus_msg})


def custom_login_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('is_authenticated', False):
            return redirect('Login') 
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def custom_admin_required(view_func):
    def _warapped_view(request, *args, **kwargs):
        if not request.session.get('is_admin', False):
            return redirect('Login')
        return view_func(request, *args, **kwargs)
    return _warapped_view 

def custom_logout(request):
    request.session['is_authenticated'] = False
    return redirect('/login') 

@custom_login_required
def list_plot(request):
    
    user_id = request.session.get('user_id')

    if request.method == 'POST':
        pimg = request.FILES.get('pimg')
        pcity = request.POST.get('pcity')
        pstate = request.POST.get('pstate')
        paddress_line = request.POST.get('add_line')
        plandmark = request.POST.get('lmark')
        area = request.POST.get('area')
        sprice = request.POST.get('sprice')
        price = request.POST.get('price')
        is_rent = request.POST.get('is-rent') == 'on'

        is_south = request.POST.get('is-south') == 'on'
        is_north = request.POST.get('is-north') == 'on'
        is_east = request.POST.get('is-east') == 'on'
        is_south_east = request.POST.get('is-south-east') == 'on'
        is_north_east = request.POST.get('is-north-east') == 'on'

        is_1 = request.POST.get('oside') == '1'
        is_2 = request.POST.get('oside') == '2'
        is_3 = request.POST.get('oside') == '3'

        has_boundary_wall = request.POST.get('wall-radio') == 'Yes'
        is_corner_plot = request.POST.get('corner-radio') == 'Yes'
        is_gated_property = request.POST.get('gated-radio') == 'Yes'

        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        smsg = request.POST.get('smsg')

        user = User.objects.get(pk=user_id)

        is_sub_user = user.is_subscribed
        
  
        plot = Plot(
            pimg=pimg,
            pcity=pcity,
            pstate=pstate,
            is_sub_user=is_sub_user,
            paddress_line=paddress_line,
            plandmark=plandmark,
            area=area,
            sprice=sprice,
            price=price,
            is_rent=is_rent,
            is_south=is_south,
            is_north=is_north,
            is_east=is_east,
            is_south_east=is_south_east,
            is_north_east=is_north_east,
            is_1=is_1,
            is_2=is_2,
            is_3=is_3,
            has_boundary_wall=has_boundary_wall,
            is_corner_plot=is_corner_plot,
            is_gated_property=is_gated_property,
            fname=fname,
            lname=lname,
            email=email,
            phone=phone,
            smsg=smsg
        )
        
        if user_id is not None:
            # Use the user_id to associate the plot with the logged-in user
            user = User.objects.get(pk=user_id)
            plot.owner = user
            plot.save()

            return redirect('Home_page')
        else:
            # Handle the case when the user is not authenticated
            return redirect('Login')

    return render(request, "list_plot.html")

@custom_login_required
def plot_page(request, id):
    plot = get_object_or_404(Plot, id=id)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message_text = request.POST.get('message')

        contact = Contact(plot=plot, name=name, email=email, phone=phone, message=message_text)
        contact.save()

        # plot_owner = plot.owner
        # plot_owner.messages.create(sender_name=name, sender_email=email, sender_phone=phone, message=message_text)

    context = {
        'plot': plot,

    }

    return render(request, 'plot_page.html', context)



def search_plots(request):
    query = request.GET.get('search-txt', '')
    print(f"Search query: {query}")

    plots = Plot.objects.all()

    # Apply search query filter
    plots = plots.filter(Q(pcity__icontains=query) | Q(pstate__icontains=query))

    # Get filter values from the form
    price_filter = request.GET.get('price-radio')
    area_filter = request.GET.get('area-radio')
    face_filter = request.GET.get('face-radio')
    rent_filter = request.GET.getlist('rent-checkbox')
    print(f"Rent Filter: {rent_filter}")

    # Initialize the filter conditions
    filter_conditions = Q()

    if 'rent' in rent_filter:
     filter_conditions &= Q(is_rent=True)

    # Add conditions based on form values
    if price_filter == '1':
        filter_conditions &= Q(price__gte=1000000, price__lte=5000000)
    elif price_filter == '2':
        filter_conditions &= Q(price__gt=5000000, price__lte=10000000)
    elif price_filter == '3':
        filter_conditions &= Q(price__gt=10000000)

    if area_filter == '4':
        filter_conditions &= Q(area__gte=0, area__lte=500)
    elif area_filter == '5':
        filter_conditions &= Q(area__gt=500, area__lte=1000)
    elif area_filter == '6':
        filter_conditions &= Q(area__gt=1000)

    if face_filter == '7':
        filter_conditions &= Q(is_east=True)
    elif face_filter == '8':
        filter_conditions &= Q(is_north=True)
    elif face_filter == '9':
        filter_conditions &= Q(is_south=True)
    elif face_filter == '10':
        filter_conditions &= Q(is_south_east=True)
    elif face_filter == '11':
        filter_conditions &= Q(is_north_east=True)
    


    # Apply the filters to the queryset
    plots = plots.filter(filter_conditions).order_by('-is_sub_user')


    
    print(plots.query)
    print(f"Query: {query}")
    print(f"Price Filter: {price_filter}")
    print(f"Area Filter: {area_filter}")
    print(f"Face Filter: {face_filter}")


    print(f"Number of plots found: {len(plots)}")
    return render(request, 'search_page.html', {'plots': plots, 'query': query})

@custom_login_required
def profile_page(request):

    user_id = request.session.get('user_id')

    if not user_id:
        # Handle the case when the user is not authenticated
        return redirect('Login')

    user_instance = get_object_or_404(User, id=user_id)

    user_plots = Plot.objects.filter(owner=user_instance)
    user_messages = Contact.objects.filter(plot__in=user_plots)

    context = {
        'user': user_instance,
        'user_plots': user_plots,
        'user_messages': user_messages,
    }


    if request.method == 'POST':
        # Get form data directly from request.POST
        new_name = request.POST.get('uname')
        new_phone = request.POST.get('uphone')
        new_email = request.POST.get('umail')

        # Update user data
        user_instance.name = new_name
        user_instance.phone = new_phone
        user_instance.email = new_email
        user_instance.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('profile_page')

    return render(request, "profile_page.html",context)

@custom_login_required
def payout_page(request):
    user_id = request.session.get('user_id')
    cus_msg = "" 


    if request.method == 'POST' and user_id is not None:
        # user = get_object_or_404(User, id=user_id)
        user = User.objects.get(id=user_id)
        print(user)

        if 'btn-pay' in request.POST and not user.is_subscribed:
            user.is_subscribed = True
            user.sub_start = datetime.now()  # Set subscription start date to current date
            user.sub_end = datetime.now() + timedelta(days=28)  
            user.save()
            return redirect('success_payment')
        else:
            cus_msg = "*You are Already Subscribed"
        

    return render(request, "payout_page.html",{'cus_msg': cus_msg})

@custom_admin_required
def imadmin(request):

    user_id = request.session.get('user_id')
    users = User.objects.all()
    aplot = Plot.objects.all()
    cc = Contact.objects.all()

    if request.method == 'POST':
        pimg = request.FILES.get('pimg')
        pcity = request.POST.get('pcity')
        pstate = request.POST.get('pstate')
        paddress_line = request.POST.get('add_line')
        plandmark = request.POST.get('lmark')
        area = int(request.POST.get('area'))
        sprice = request.POST.get('sprice')
        price = request.POST.get('price')
        is_rent = request.POST.get('is-rent') == 'on'

        is_south = request.POST.get('is-south') == 'on'
        is_north = request.POST.get('is-north') == 'on'
        is_east = request.POST.get('is-east') == 'on'
        is_south_east = request.POST.get('is-south-east') == 'on'
        is_north_east = request.POST.get('is-north-east') == 'on'

        is_1 = request.POST.get('oside') == '1'
        is_2 = request.POST.get('oside') == '2'
        is_3 = request.POST.get('oside') == '3'

        has_boundary_wall = request.POST.get('wall-radio') == 'Yes'
        is_corner_plot = request.POST.get('corner-radio') == 'Yes'
        is_gated_property = request.POST.get('gated-radio') == 'Yes'

        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        smsg = request.POST.get('smsg')
        if 'btn-plot' in request.POST:
    
            plot = Plot(
                pimg=pimg,
                pcity=pcity,
                pstate=pstate,
                paddress_line=paddress_line,
                plandmark=plandmark,
                area=area,
                sprice=sprice,
                price=price,
                is_rent=is_rent,
                is_south=is_south,
                is_north=is_north,
                is_east=is_east,
                is_south_east=is_south_east,
                is_north_east=is_north_east,
                is_1=is_1,
                is_2=is_2,
                is_3=is_3,
                has_boundary_wall=has_boundary_wall,
                is_corner_plot=is_corner_plot,
                is_gated_property=is_gated_property,
                fname=fname,
                lname=lname,
                email=email,
                phone=phone,
                smsg=smsg
            )
            
            if user_id is not None:
                # Use the user_id to associate the plot with the logged-in user
                user = User.objects.get(pk=user_id)
                plot.owner = user
                plot.save()

                return redirect(reverse('imadmin'))
       
        elif 'btn-update' in request.POST:
            pid = request.POST.get('pid')  # Assuming a hidden input field for pid

            try:
                plot = Plot.objects.get(id=pid)

                # Update record fields
                if pimg is not None:
                    plot.pimg = pimg
                if pcity is not None:
                    plot.pcity = pcity
                if pstate is not None:
                    plot.pstate = pstate
                if paddress_line is not None:
                    plot.paddress_line = paddress_line
                if plandmark is not None:
                    plot.plandmark = plandmark
                if area is not None:
                    plot.area = int(area)
                if sprice is not None:
                    plot.sprice = sprice
                if price is not None:
                    plot.price = price
                if is_rent is not None:
                    plot.is_rent = is_rent
                if is_south is not None:
                    plot.is_south = is_south
                if is_north is not None:
                    plot.is_north = is_north
                if is_east is not None:
                    plot.is_east = is_east
                if is_south_east is not None:
                    plot.is_south_east = is_south_east
                if is_north_east is not None:
                    plot.is_north_east = is_north_east
                if is_1 is not None:
                    plot.is_1 = is_1
                if is_2 is not None:
                    plot.is_2 = is_2
                if is_3 is not None:
                    plot.is_3 = is_3
                if has_boundary_wall is not None:
                    plot.has_boundary_wall = has_boundary_wall
                if is_corner_plot is not None:
                    plot.is_corner_plot = is_corner_plot
                if is_gated_property is not None:
                    plot.is_gated_property = is_gated_property
                if fname is not None:
                    plot.fname = fname
                if lname is not None:
                    plot.lname = lname
                if email is not None:
                    plot.email = email
                if phone is not None:
                    plot.phone = phone
                if smsg is not None:
                    plot.smsg = smsg

                plot.save()

                return redirect(reverse('imadmin'))

            except Plot.DoesNotExist:
                # Handle case where the record doesn't exist
                return render(request, "admin_page.html", {'error': 'Invalid plot ID'})

       

    return render(request, "admin_page.html", {'users': users, 'aplot': aplot, 'cc': cc})

def del_user(request):

    if request.method == "POST":
        uid = request.POST.get('uid')
        pid = request.POST.get('pid')
        uname = request.POST.get('uname')
        umail = request.POST.get('umail')
        uphone = request.POST.get('uphone')
        start = request.POST.get('start')
        end = request.POST.get('end')

        btn_update = request.POST.get('btn-update')
        btn_re = request.POST.get('reset')
        btn_del = request.POST.get('btn-del')
        try:
            user = User.objects.get(id=uid)

            if btn_del is not None:
                user.delete()
            elif btn_update is not None:
            # Check if the checkbox is checked
                user.is_subscribed = request.POST.get('is-subscribed') == 'on'
                user.is_admin = request.POST.get('is-admin') == 'on'
                user.name = uname
                user.email = umail
                user.sub_start = start
                user.sub_end = end
            elif btn_re is not None:
                   # Get all subscribed users whose subscription end date is today
                users_to_unsubscribe = User.objects.filter(is_subscribed=True, sub_end=timezone.now().date())
            # Unsubscribe the users
                for user in users_to_unsubscribe:
                    user.is_subscribed = False
                    user.save()
            if user.sub_end:
                try:
                    sub_end_date = datetime.strptime(user.sub_end, '%Y-%m-%d').date()
                    if sub_end_date < timezone.now().date():
                        user.is_subscribed = False
                except ValueError:
                    # Handle the case where user.sub_end is not in the expected format
                    pass
            elif not user.sub_start:
                    user.sub_start = timezone.now().date()
                    user.sub_end = timezone.now().date() + timedelta(days=30)
            user.phone = uphone
            user.save()
                 
        except User.DoesNotExist:

         pass
     
    call_command('update_subscriptions')
    return  redirect(reverse('imadmin'))

def udel(request):
    
    if request.method == "POST":
        
        pid = request.POST.get('bid')
        btn_del = request.POST.get('btn-del')
        user = User.objects.get(id=pid)
        
        if btn_del is not None:
       
            user.delete()
            
    return  redirect(reverse('imadmin'))
      


def del_plot(request):
    if request.method == "POST":
        pid = request.POST.get('pid')
        btn_up = request.POST.get('btn-update-p')
        btn_delp = request.POST.get('btn-del-p')
        try:

           plot = Plot.objects.get(id=pid)
           if btn_up is not None:
                plot.is_rent = request.POST.get('is-rent') == 'on'
                plot.is_south = request.POST.get('is-south') == 'on'
                plot.is_north = request.POST.get('is-north') == 'on'
                plot.is_east = request.POST.get('is-east') == 'on'
                plot.is_north_east = request.POST.get('is-north-east') == 'on'
                plot.is_south_east = request.POST.get('is-south-east') == 'on'
                plot.has_boundary_wall = request.POST.get('is-boundary') == 'on'
                plot.is_corner_plot = request.POST.get('is_corner') == 'on'
                plot.is_gated_property = request.POST.get('is-gated') == 'on'
                plot.is_sub_user = request.POST.get('is_sub_user') == 'on'
                plot.save()

           elif btn_delp is not None:
               plot.delete()
                 
        except User.DoesNotExist:

         pass

    return  redirect(reverse('imadmin'))

@custom_login_required
def success_payment(request):

    return render(request, "success_payment.html")

def exclusive_page(request):

    return render(request, "exclusive.html")

def buy_page(request):

    return render(request, "buy_page.html")

def rent_page(request):

    return render(request, "rent_page.html")

def about(request):

    return render(request, "about.html")

def contact(request):
    name = request.POST.get('name')
    mail = request.POST.get('mail')
    phone = request.POST.get('phone')
    msg = request.POST.get('msg')

    if request.method == "POST":

        try:
            con = Conus.objects.all()

            con = Conus(
                name=name,
                email=mail,
                phone=phone,
                message=msg
            )

            con.save()
            return redirect('contact')
        except Conus.DoesNotExist:

            pass


    return render(request, "contact.html")

def terms(request):

    return render(request, "terms_con.html")

def policy(request):

    return render(request, "policy.html")

def sell_page(request):

    return render(request, "sell_page.html")

def reset(request):

    if request.method == "POST":
        old_password = request.POST.get('oldpass')
        new_password = request.POST.get('newpass')
        user_id = request.session.get('user_id')

        print(f"Old Password: {old_password}")
        print(f"New Password: {new_password}")

        if user_id:
            # Retrieve the user from the database using the user_id from the session
            user = User.objects.get(id=user_id)

            # Check if the old password matches the stored hashed password
            if check_password(old_password, user.password):
                # Update the password with the new hashed password
                user.password = make_password(new_password)
                user.save()
                custom_logout(request)
                cus_msg = '~ password changed successfully'
                return redirect('Login')
            else:
                cus_msg = '~ old password is incorrect.'
                return render(request, "reset.html", {'cus_msg': cus_msg})
        else:
            cus_msg = '~ user ID not found in the session.'
            return render(request, "reset.html", {'cus_msg': cus_msg})



    return render(request, "reset.html")

