from django.shortcuts import render, HttpResponse
from django.contrib.auth.hashers import make_password
from .models import login
from userApp.models import TravellerProfile
# Create your views here.
def guestHome(request):
    return render(request, 'guest/index.html')
def regn_select(request):
    return render(request, 'guest/register_select.html')
def traveller_regn(request):
    return render(request, 'guest/traveller_regn.html')
def login_view(request):
    return render(request, 'guest/loginpage.html')

def traveller_regn(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        pincode = request.POST.get('pincode')
        city = request.POST.get('city')

        if login.objects.filter(username=username).exists():
            return HttpResponse('<script>alert("Username already exists! Please choose a different username."); window.location.href="/traveller-register/";</script>')
        
        lob = login()
        lob.username = username
        lob.password = password
        lob.role = 'traveller'
        lob.status = 'active'
        lob.save()

        tob = TravellerProfile()
        tob.traveller_name = name
        tob.email = email
        tob.phone = phone
        tob.address = address
        tob.pincode = pincode
        tob.city = city
        tob.login = lob
        tob.save()

        return HttpResponse('<script>alert("Registration successful! Please login to continue."); window.location.href="/login/";</script>')
    
    return render(request, 'guest/traveller_regn.html')
