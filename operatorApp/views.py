from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.core.exceptions import ValidationError
from adminApp.models import District, Location, Accessibility
from guestApp.models import Operator
from .models import Tour, TourAccessibility, TourImages

# Create your views here.
def operator_home(request):
    return render(request, 'operator/operator_home.html')
    
def tour_regn_view(request):
    districts = District.objects.all()
    locations = Location.objects.all().order_by('name')
    accessibilities = Accessibility.objects.all()
    return render(request, 'operator/tour_regn.html', {'districts': districts, 'locations': locations, 'accessibilities': accessibilities})

def filllocations(request):
    did = int(request.POST.get("did"))
    location = Location.objects.filter(district=did).values('location_id', 'name')
    return JsonResponse(list(location), safe=False)

def tour_regn_insert(request):
    if request.method == "POST":
        tour_name = request.POST.get("tour_name")
        location_id = request.POST.get("location")
        description = request.POST.get("description")
        price_per_person = request.POST.get("price")
        duration_days = request.POST.get("duration")
        itinerary = request.FILES.get("itinerary")
        max_persons = request.POST.get("max_persons")
        tour_acc_list = request.POST.getlist("accessibility")
        tour_image_files = request.FILES.getlist("tour_images")

        login_id = request.session.get('login_id')

        # Validate login_id exists in session
        if not login_id:
            return HttpResponse("<script>alert('Error: Operator session expired. Please log in again.');window.location.href='/login/';</script>")
        
        try:
            operator = Operator.objects.get(login_id=login_id)
        except Operator.DoesNotExist:
            return HttpResponse("<script>alert('Error: Operator account not found. Please contact support.');window.location.href='/login/';</script>")
        
        tour = Tour()
        tour.tour_name = tour_name
        tour.location = Location.objects.get(location_id=location_id)
        tour.description = description
        tour.price = float(price_per_person)
        tour.duration_days = duration_days
        tour.tour_itinerary = itinerary
        tour.max_persons = int(max_persons)
        tour.operator = operator
        tour.save()
        
        for image in tour_image_files:
            tour_images = TourImages()
            tour_images.image = image
            tour_images.tour = tour
            tour_images.save()
        
        for acc in tour_acc_list:
            tour_acc = TourAccessibility()
            tour_acc.accessibility = Accessibility.objects.get(accessibility_id=acc)
            tour_acc.tour = tour
            tour_acc.save()
        
        return HttpResponse("<script>alert('Tour registered successfully');window.location.href='/operator-home/tour-regn-view/';</script>")
    return redirect('/operator-home/tour-regn-view/')