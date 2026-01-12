from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *

# Create your views here.
def adminHome(request):
    return render(request, 'adminT/index.html')
def distRegn(request):
    return render(request, 'adminT/districtRegn.html')

def distRegnInsert(request):
    if request.method == 'POST':
        district = request.POST.get('district')
        # check against the model field name (it's `name`, not `district`)
        if District.objects.filter(name=district).exists():
            return HttpResponse("<script>alert('Already exists!!!');window.location.href ='/distRegn/';</script>")
        dob = District()
        dob.name = district
        dob.save()
        return HttpResponse("<script>alert('District added successfully!!!');window.location.href ='/distRegn/';</script>")
    return HttpResponse("Invalid request")

def distView(request):
    districts = District.objects.all().order_by('name')
    return render(request, 'adminT/districtView.html', {'districts':districts})

def distDelete(request, id):
    district = District.objects.get(district_id=id)
    district.delete()
    return HttpResponse("<script>alert('District deleted successfully!!!');window.location.href ='/distView/';</script>")

def distEdit(request,id):
    if request.method=='POST':
        districtname=request.POST.get("districtname")
        dis = District.objects.get(district_id=id)
        dis.name = districtname
        dis.save()
        return HttpResponse("<script>alert('District updated successfully!!!');window.location.href ='/distView/';</script>")
    district = District.objects.get(district_id=id)
    return render(request,"adminT/districtEdit.html",{'district':district})

def locationRegn(request):
    districts = District.objects.all()
    return render(request, 'adminT/locationRegn.html', {'districts': districts})

def locationInsert(request):
    if request.method == "POST":
        district_id = request.POST.get("did")
        lname = request.POST.get("lname")
        lob = Location()
        lob.name = lname
        lob.district_id = District.objects.get(district_id=district_id)
        if Location.objects.filter(name=lname, district_id=district_id).exists():
            return HttpResponse("<script>alert('Already Exists..');window.location='locationRegn/';</script>")
        else:
            lob.save() 
            return HttpResponse("<script>alert('Location inserted successfully');window.location='/locationView/';</script>")
        
def locationView(request):
    locations = Location.objects.all().order_by('name')
    return render(request, 'adminT/locationView.html', {'locationdata': locations})