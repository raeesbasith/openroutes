from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.core.exceptions import ValidationError

from adminApp.models import District, Location

# Create your views here.
def operator_home(request):
    return render(request, 'operator/operator_home.html')

def validate_pdf(file):
    if not file.name.endswith('.pdf'):
        raise ValidationError("Only PDF files are allowed.")
    
def tour_regn_view(request):
    districts = District.objects.all()
    locations = Location.objects.all().order_by('name')
    return render(request, 'operator/tour_regn.html', {'districts': districts, 'locations': locations})

def filllocations(request):
    did = int(request.POST.get("did"))
    location = Location.objects.filter(district=did).values('location_id', 'name')
    return JsonResponse(list(location), safe=False)
"""
def tour_regn_insert(request):
    if request.method == "POST":
        tour_name = request.POST.get("tour_name")
        location_id = request.POST.get("location")
        description = request.POST.get("description")
        price_per_person = request.POST.get("price")
        duration_days = request.POST.get("duration")
"""
