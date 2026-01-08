from django.shortcuts import render, HttpResponse
from django.contrib.auth.hashers import make_password
from .models import login
# Create your views here.
def guestHome(request):
    return render(request, 'guest/index.html')
def regn(request):
    return render(request, 'guest/regnpage.html')
def login_view(request):
    return render(request, 'guest/loginpage.html')

def regn_insert(request):
    if request.method == "POST":
        username = request.POST.get("username")
        # check if username already exists
        if login.objects.filter(username=username).exists():
            return HttpResponse("<script>alert('Already exists!!!'); window.location = '/regn/';</script>")

        name = request.POST.get('name','')
        phone = request.POST.get('phone','')
        email = request.POST.get('email','')
        password = request.POST.get('password','')
        role = request.POST.get('role','')

        lob = login()
        lob.full_name = name
        lob.phone = phone
        lob.email = email
        lob.username = username
        lob.password = make_password(password)
        lob.role = role
        lob.save()
        return HttpResponse("<script>alert('District added successfully'); window.location='/regn/';</script>")

    return HttpResponse("Invalid request")