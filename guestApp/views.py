from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password
from .models import login, Operator
from .models import TravellerProfile
from adminApp.models import District
from email.message import EmailMessage
import smtplib

# Create your views here.

def guestHome(request):
    return render(request, 'guest/index.html')
def regn_select(request):
    return render(request, 'guest/register_select.html')
def traveller_regn(request):
    return render(request, 'guest/traveller_regn.html')
def login_view(request):
    return render(request, 'guest/loginpage.html')

def login_insert(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        logindata = login.objects.filter(username=username).first()

        if logindata:
            if logindata.password == password:
                request.session['login_id'] = logindata.login_id
                role = logindata.role
                status = logindata.status
                if role == 'admin':
                    return redirect('/admin-home/')
                elif role == 'traveller':
                    if status == 'active':
                        return redirect('/traveller-home/')
                    else:
                        return HttpResponse('<script>alert("Your account is temporarily blocked. Please contact support."); window.location.href="/login/";</script>')
                elif role == 'operator':
                    if status == 'active':    
                        return redirect('/operator-home/')
                    else:
                        return HttpResponse('<script>alert("Your operator account is under review. Please wait for approval."); window.location.href="/login/";</script>')
            else:
                return HttpResponse('<script>alert("Invalid password! Please try again."); window.location.href="/login/";</script>')
        return render(request, 'guest/loginpage.html', {'error': 'Invalid username! Please try again.'})
    return render(request, 'guest/loginpage.html')
                    

def traveller_regn(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        district_id = request.POST.get('districtid')
        pincode = request.POST.get('pincode')
        city = request.POST.get('city')

        if login.objects.filter(username=username).exists():
            return HttpResponse('<script>alert("Username already exists! Please choose a different username."); window.location.href="/traveller-register/";</script>')
        
        if TravellerProfile.objects.filter(email=email).exists():
             return HttpResponse('<script>alert("Email already registered! Please use a different email."); window.location.href="/traveller-register/";</script>')

        try:
            lob = login()
            lob.username = username
            lob.password = password
            lob.role = 'traveller'
            lob.status = 'active'
            lob.save()

            district = District.objects.get(district_id=district_id)
            tob = TravellerProfile()
            tob.traveller_name = name
            tob.email = email
            tob.phone = phone
            tob.address = address
            tob.district = district
            tob.pincode = pincode
            tob.city = city
            tob.login = lob
            tob.save()

            # Send Welcome Email
            try:
                msg = EmailMessage()
                msg.set_content(f"""
Hello {name},

Welcome to OpenRoutes!

Your traveller account has been successfully created. You can now log in and explore our accessible tour packages.

Username: {username}

Happy Travels!
The OpenRoutes Team
""")
                msg['Subject'] = "Welcome to OpenRoutes - Registration Successful"
                msg['From'] = 'raeesbasith15@gmail.com'
                msg['To'] = email
                
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login('raeesbasith15@gmail.com', 'qfac dtcm rsbb pwyg')
                    smtp.send_message(msg)
                    print(f"Welcome email sent to {email}")
            except Exception as e:
                print(f"Error sending welcome email: {e}")
                # Don't fail registration if email fails, just log it

            return HttpResponse('<script>alert("Registration successful! Please login to continue."); window.location.href="/login/";</script>')
            
        except Exception as e:
            return HttpResponse(f'<script>alert("Error during registration: {str(e)}"); window.history.back();</script>')
    
    districts = District.objects.all()
    return render(request, 'guest/traveller_regn.html', {'districts': districts})

def operator_regn(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        operator_name = request.POST.get('name')
        contact = request.POST.get('phone')
        address = request.POST.get('address')
        email = request.POST.get('email')
        Email=request.POST.get('email')  # to address
        msg = EmailMessage()
        msg.set_content('Body')
        msg['Subject'] = "Registration Completed"
        msg['from'] = 'raeesbasith15@gmail.com'
        msg['To'] = {Email}
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login('raeesbasith15@gmail.com','qfac dtcm rsbb pwyg')
            smtp.send_message(msg)

        district_id = request.POST.get('districtid')
        license_file = request.FILES.get('license')

        if login.objects.filter(username=username).exists():
            return HttpResponse('<script>alert("Username already exists! Please choose a different username."); window.location.href="/operator-register/";</script>')
        
        lob = login()
        lob.username = username
        lob.password = password
        lob.role = 'operator'
        lob.status = 'requested'

        district = District.objects.get(district_id=district_id)

        oob = Operator()
        oob.operator_name = operator_name
        oob.contact = contact
        oob.address = address
        oob.email = email
        oob.district = district
        oob.status = 'requested'
        oob.license = license_file
        oob.login = lob
        lob.save()
        oob.save()

        return HttpResponse('<script>alert("Registration request submitted! Your account is under review."); window.location.href="/guest/";</script>')
    districts = District.objects.all()    
    return render(request, 'guest/operator_regn.html', {'districts': districts})

def logout_view(request):
    request.session.flush()
    return redirect('guest')
