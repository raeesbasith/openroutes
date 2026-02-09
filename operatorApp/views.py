from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.core.exceptions import ValidationError
from django.views.decorators.cache import cache_control
from adminApp.models import District, Location, Accessibility
from guestApp.models import Operator
from userApp.models import Booking
from .models import Tour, TourAccessibility, TourImages

# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def operator_home(request):
    login_id = request.session.get('login_id')
    
    if not login_id:
        return redirect('/login/')
        
    context = {}
    if login_id:
        try:
            operator = Operator.objects.get(login_id=login_id)
            context['operator'] = operator
        except Operator.DoesNotExist:
            pass
            
    return render(request, 'operator/operator_home.html', context)

def tour_view(request):
    login_id = request.session.get('login_id')
    if not login_id:
        return redirect('/login/')
        
    try:
        operator = Operator.objects.get(login_id=login_id)
        tours = Tour.objects.filter(operator=operator).order_by('-created_at')
        return render(request, 'operator/view_packages.html', {'tours': tours})
    except Operator.DoesNotExist:
        return redirect('/login/')

def delete_package(request, tour_id):
    login_id = request.session.get('login_id')
    if not login_id:
        return redirect('/login/')
        
    try:
        operator = Operator.objects.get(login_id=login_id)
        tour = Tour.objects.get(tour_id=tour_id, operator=operator)
        tour.delete()
        return HttpResponse("<script>alert('Package deleted successfully');window.location.href='/operator-home/tour-view/';</script>")
    except (Operator.DoesNotExist, Tour.DoesNotExist):
        return HttpResponse("<script>alert('Error: Could not delete package.');window.location.href='/operator-home/tour-view/';</script>")
    
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
        extra_cost = request.POST.get("extra_cost")

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
            extra_cost = request.POST.get("extra_cost_" + str(acc))
            if extra_cost:
                tour_acc.extra_cost_per_acc = float(extra_cost)
            tour_acc.save()
        
        return HttpResponse("<script>alert('Tour registered successfully');window.location.href='/operator-home/tour-regn-view/';</script>")
    return redirect('/operator-home/tour-regn-view/')

def edit_package(request, tour_id):
    login_id = request.session.get('login_id')
    if not login_id:
        return redirect('/login/')
    
    try:
        operator = Operator.objects.get(login_id=login_id)
        tour = Tour.objects.get(tour_id=tour_id, operator=operator)
    except (Operator.DoesNotExist, Tour.DoesNotExist):
        return redirect('/operator-home/tour-view/')

    if request.method == "POST":
        tour.tour_name = request.POST.get("tour_name")
        location_id = request.POST.get("location")
        if location_id:
            tour.location = Location.objects.get(location_id=location_id)
        tour.description = request.POST.get("description")
        tour.price = float(request.POST.get("price"))
        tour.duration_days = request.POST.get("duration")
        tour.max_persons = int(request.POST.get("max_persons"))
        
        itinerary = request.FILES.get("itinerary")
        if itinerary:
            tour.tour_itinerary = itinerary
            
        tour.save()

        # Handle Images (Append new ones)
        tour_image_files = request.FILES.getlist("tour_images")
        for image in tour_image_files:
            tour_images = TourImages(image=image, tour=tour)
            tour_images.save()
            
        # Handle Accessibility
        selected_acc_ids = request.POST.getlist("accessibility")
        TourAccessibility.objects.filter(tour=tour).delete()
        
        for acc_id in selected_acc_ids:
            acc = Accessibility.objects.get(accessibility_id=acc_id)
            extra_cost = request.POST.get(f"extra_cost_{acc_id}")
            tour_acc = TourAccessibility(tour=tour, accessibility=acc)
            if extra_cost:
                tour_acc.extra_cost_per_acc = float(extra_cost)
            tour_acc.save()
            
        return HttpResponse("<script>alert('Package updated successfully');window.location.href='/operator-home/tour-view/';</script>")

    # GET request
    districts = District.objects.all()
    current_district_id = tour.location.district.district_id
    locations = Location.objects.filter(district_id=current_district_id).order_by('name')
    accessibilities = Accessibility.objects.all()
    
    existing_accs = TourAccessibility.objects.filter(tour=tour)
    
    # Map {acc_id: cost}
    existing_map = {acc.accessibility.accessibility_id: acc.extra_cost_per_acc for acc in existing_accs}

    acc_list = []
    for acc in accessibilities:
        is_checked = acc.accessibility_id in existing_map
        cost = existing_map.get(acc.accessibility_id, "")
        acc_list.append({
            'accessibility_id': acc.accessibility_id,
            'accessibility_name': acc.accessibility_feature,
            'is_checked': is_checked,
            'cost': cost
        })

    return render(request, 'operator/package_edit.html', {
        'tour': tour,
        'districts': districts,
        'locations': locations, 
        'acc_list': acc_list,
        'current_district_id': current_district_id,
        'existing_images': TourImages.objects.filter(tour=tour)
    })

def delete_tour_image(request, image_id):
    login_id = request.session.get('login_id')
    if not login_id:
        return JsonResponse({'status': 'error', 'message': 'Not logged in'})
    
    try:
        img = TourImages.objects.get(tour_image_id=image_id)
        # Check ownership logic if necessary, here we assume getting by ID is safe enough or adding extra checks
        # Ideally check if img.tour.operator.login_id == login_id
        if img.tour.operator.login_id == login_id:
            img.delete()
            return JsonResponse({'status': 'success'})
        else:
             return JsonResponse({'status': 'error', 'message': 'Unauthorized'})
    except TourImages.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Image not found'})

def package_single_view(request, tour_id):
    login_id = request.session.get('login_id')
    if not login_id:
        return redirect('login')
        
    try:
        operator = Operator.objects.get(login_id=login_id)
        tour = Tour.objects.get(tour_id=tour_id, operator=operator)
        images = TourImages.objects.filter(tour=tour)
        accessibility_features = TourAccessibility.objects.filter(tour=tour).select_related('accessibility')
        
        context = {
            'tour': tour,
            'images': images,
            'accessibility_features': accessibility_features
        }
        return render(request, 'operator/package_singleView.html', context)
    except (Operator.DoesNotExist, Tour.DoesNotExist):
        return redirect('tour_view')

def booking_view(request):
    login_id = request.session.get('login_id')
    if not login_id:
        return redirect('login')
    
    try:
        operator = Operator.objects.get(login_id=login_id)
        # Fetch bookings for tours created by this operator
        bookings = Booking.objects.filter(tour__operator=operator).select_related('traveller', 'tour').order_by('-booking_date')
        
        return render(request, 'operator/booking_view.html', {'bookings': bookings})
    except Operator.DoesNotExist:
        return redirect('login')

def update_booking_status(request, booking_id):
    login_id = request.session.get('login_id')
    if not login_id:
        return JsonResponse({'status': 'error', 'message': 'Not logged in'})
        
    if request.method == 'POST':
        new_status = request.POST.get('status')
        try:
            operator = Operator.objects.get(login_id=login_id)
            booking = Booking.objects.get(booking_id=booking_id, tour__operator=operator)
            booking.booking_status = new_status
            booking.save()
            return JsonResponse({'status': 'success'})
        except (Operator.DoesNotExist, Booking.DoesNotExist):
            return JsonResponse({'status': 'error', 'message': 'Booking not found or unauthorized'})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def profile_view(request):
    login_id = request.session.get('login_id')
    if not login_id:
        return redirect('login')
    
    try:
        operator = Operator.objects.get(login_id=login_id)
        return render(request, 'operator/profile_view.html', {'operator': operator})
    except Operator.DoesNotExist:
        return redirect('login')

