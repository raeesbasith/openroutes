from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import *
from operatorApp.models import Operator
from guestApp.models import login

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
    districts = District.objects.all().order_by('name')
    locations = Location.objects.all().order_by('name')
    return render(request, 'adminT/locationView.html', {'districts': districts, 'locationdata': locations})

def locationDelete(request, id):
    location = Location.objects.get(location_id=id)
    location.delete()
    return HttpResponse("<script>alert('Location deleted successfully!!!');window.location.href ='/locationView/';</script>")

def locationEdit(request,id):
    if request.method == 'POST':
        locationname = request.POST.get("locationname")
        loc = Location.objects.get(location_id=id)
        loc.name = locationname
        loc.save()
        return HttpResponse("<script>alert('Location updated successfully!!!');window.location.href ='/locationView/';</script>")
    location = Location.objects.get(location_id=id)
    return render(request,"adminT/locationEdit.html",{'location':location})

def filllocation(request):
    try:
        did = int(request.POST.get("did"))
        location = Location.objects.filter(district_id=did).values('location_id', 'name')
        return JsonResponse(list(location), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def disabilityRegn(request):
    return render(request, 'adminT/disabilityRegn.html')
def disabilityInsert(request):
    if request.method == 'POST':
        disability = request.POST.get('disability')
        if Disability.objects.filter(disability_type=disability).exists():
            return HttpResponse("<script>alert('Already exists!!!');window.location.href ='/disabilityRegn/';</script>")
        dob = Disability()
        dob.disability_type = disability
        dob.save()
        return HttpResponse("<script>alert('Disability added successfully!!!');window.location.href ='/disabilityView/';</script>")
    return HttpResponse("Invalid request")

def disabilityView(request):
    disabilities = Disability.objects.all().order_by('disability_type')
    return render(request, 'adminT/disabilityView.html', {'disabilities':disabilities})

def disabilityDelete(request, id):
    disability = Disability.objects.get(disability_id=id)
    disability.delete()
    return HttpResponse("<script>alert('Disability deleted successfully!!!');window.location.href ='/disabilityView/';</script>")

def disabilityEdit(request,id):
    if request.method=='POST':
        disabilitytype=request.POST.get("disabilitytype")
        dis = Disability.objects.get(disability_id=id)
        dis.disability_type = disabilitytype
        dis.save()
        return HttpResponse("<script>alert('Disability updated successfully!!!');window.location.href ='/disabilityView/';</script>")
    disability = Disability.objects.get(disability_id=id)
    return render(request,"adminT/disabilityEdit.html",{'disability':disability})

def accessibilityRegn(request):
    return render(request, 'adminT/accessibilityRegn.html')

def accessibilityInsert(request):
    if request.method == 'POST':
        accessibility = request.POST.get('accessibility')
        if Accessibility.objects.filter(accessibility_feature=accessibility).exists():
            return HttpResponse("<script>alert('Already exists!!!');window.location.href ='/accessibilityRegn/';</script>")
        aob = Accessibility()
        aob.accessibility_feature = accessibility
        aob.save()
        return HttpResponse("<script>alert('Accessibility feature added successfully!!!');window.location.href ='/accessibilityView/';</script>")
    return HttpResponse("Invalid request")

def accessibilityView(request):
    accessibilities = Accessibility.objects.all().order_by('accessibility_feature')
    return render(request, 'adminT/accessibilityView.html', {'accessibilities':accessibilities})

def accessibilityDelete(request, id):
    accessibility = Accessibility.objects.get(accessibility_id=id)
    accessibility.delete()
    return HttpResponse("<script>alert('Accessibility feature deleted successfully!!!');window.location.href ='/accessibilityView/';</script>")

def accessibilityEdit(request,id):
    if request.method=='POST':
        accessibilityfeature=request.POST.get("accessibilityfeature")
        acc = Accessibility.objects.get(accessibility_id=id)
        acc.accessibility_feature = accessibilityfeature
        acc.save()
        return HttpResponse("<script>alert('Accessibility feature updated successfully!!!');window.location.href ='/accessibilityView/';</script>")
    accessibility = Accessibility.objects.get(accessibility_id=id)
    return render(request,"adminT/accessibilityEdit.html",{'accessibility':accessibility})

def operatorVerification(request):
    operators = Operator.objects.filter(status='requested').order_by('operator_id')
    return render(request, 'adminT/operatorVerification.html', {'operators': operators})

def licenseView(request, id):
    operator = Operator.objects.get(operator_id=id)
    return render(request, 'adminT/licenseView.html', {'operator': operator})

def operatorApprove(request, id):
    operator = Operator.objects.get(operator_id=id)
    operator.status = 'approved'
    operator.save()
    return HttpResponse("<script>alert('Operator approved!!!'); window.location.href = '/operator-verification/';</script>")

def operatorReject(request, id):
    operator = Operator.objects.get(operator_id=id)
    operator.status = 'rejected'
    operator.save()
    return HttpResponse("<script>alert('Operator rejected!!!'); window.location.href = '/operator-verification/';</script>")