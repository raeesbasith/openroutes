from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_control
from adminApp.models import District, Location, Accessibility
from operatorApp.models import Tour, TourAccessibility, TourImages
from userApp.models import *
from guestApp.models import *
import uuid
from django.db.models import Case, When, Value, IntegerField
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def traveller_home(request):
    if request.session.get('login_id'):
        return render(request, 'traveller/traveller_home.html')
    else:
        return redirect('login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def tour_packages_view(request):
    if not request.session.get('login_id'):
        return redirect('login')

    Districts = District.objects.all()
    accessibilities = Accessibility.objects.all()
    # Base queryset
    Tour_list = Tour.objects.all().order_by('price')

    # Apply filters from GET params
    district = request.GET.get('district')
    location = request.GET.get('location')
    access_list = request.GET.getlist('accessibility')

    if district:
        Tour_list = Tour_list.filter(location__district__district_id=district)

    if location:
        Tour_list = Tour_list.filter(location__location_id=location)

    # If accessibilities selected, require tours that have ALL selected features
    # (chaining filters reduces to intersection)
    for acc in access_list:
        if acc:
            Tour_list = Tour_list.filter(touraccessibility__accessibility__accessibility_id=acc)

    paginator = Paginator(Tour_list.distinct(), 10)  # 10 tours per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'traveller/tour_packages.html', {
        'Districts': Districts,
        'accessibilities': accessibilities,
        'Tour': page_obj
    })

# Removed duplicate view `tour_details` to avoid confusion; use `tour_detail` below.

def filllocation(request):
    did = request.POST.get('did')
    locations = Location.objects.filter(district_id=did).values('location_id', 'name')
    return JsonResponse(list(locations), safe=False)

def chatbot_api(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        user_message = data.get('message', '')

        
        google_api_key = "AIzaSyCIcgQE4YX0a-cdCEI14NX4G40VgliOAHM" # 'YOUR_GOOGLE_GEMINI_API_KEY'
        
        if google_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=google_api_key)
                
                # Function to try generation with a specific model
                def generate(model_name):
                    model = genai.GenerativeModel(model_name)
                    # Context prompt
                    context = "You are a helpful assistant for a travel agency website called OpenRoutes that specializes in accessible tourism for people with disabilities. Keep answers concise and helpful."
                    full_prompt = f"{context}\n\nUser: {user_message}"
                    return model.generate_content(full_prompt).text

                try:
                    # Try the fast, free model first
                    ai_reply = generate('gemini-1.5-flash')
                except Exception as e1:
                    # If that fails (e.g. 404), try to find ANY supported model
                    if "404" in str(e1) or "not found" in str(e1):
                        found_model = None
                        for m in genai.list_models():
                            if 'generateContent' in m.supported_generation_methods:
                                found_model = m.name
                                break
                        
                        if found_model:
                             ai_reply = generate(found_model)
                        else:
                             raise e1 # Re-raise if we couldn't find a fallback
                    else:
                        raise e1
                
            except Exception as e:
                ai_reply = f"Error communicating with AI: {str(e)}"
        else:
            # Simulated response for demonstration without API Key
            ai_reply = f"I am a friendly AI assistant for OpenRoutes (Powered by Gemini). You asked: '{user_message}'. I can help you find accessible tours. (Please configure the Google Gemini API key in userApp/views.py to get real AI answers)"

        return JsonResponse({'reply': ai_reply})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def tour_detail(request, tour_id):
    tour = get_object_or_404(Tour, tour_id=tour_id)
    return render(request, 'traveller/tour_detail.html', {'tour': tour})

def booking(request, tour_id):
    tour = Tour.objects.get(tour_id=tour_id)
    accessibilities = TourAccessibility.objects.filter(tour=tour_id)
    return render(request, 'traveller/booking.html', {'tour': tour, 'accessibilities': accessibilities})

def calculate_booking_amount(tour, total_people, accessibility_selections_per_person):
    base_amount = tour.price * total_people
    acc_cost = 0

    # accessibility_selections_per_person is a list of lists of accessibility IDs
    for person_selections in accessibility_selections_per_person:
        for acc in person_selections:
            try:
                ta = TourAccessibility.objects.get(tour=tour, accessibility_id=acc)
                acc_cost += ta.extra_cost_per_acc
            except TourAccessibility.DoesNotExist:
                continue

    total_amount = base_amount + acc_cost
    return base_amount, acc_cost, total_amount

def booking_confirm(request, tour_id):
    if request.method == 'POST':
        login_id = request.session.get('login_id')
        if not login_id:
            return HttpResponse("<script>alert('Error: User session expired. Please log in again.');window.location.href='/login/';</script>")
        
        try:
            traveller = TravellerProfile.objects.get(login=login_id)
        except TravellerProfile.DoesNotExist:
            return HttpResponse("<script>alert('Error: Traveller profile not found. Please ensure you are logged in as a traveller.');window.location.href='/login/';</script>")
        
        tour = Tour.objects.get(tour_id=tour_id)
        total_persons = int(request.POST.get('total_persons'))
        persons_needing_accessibility = int(request.POST.get('persons_needing_accessibility', 0))
        caregiver_gender = request.POST.get('caregiver_gender_preference', None)
        tour_date = request.POST.get('tour_date')

        # Collect accessibility selections per person based on the count provided
        accessibility_selections_per_person = []
        if persons_needing_accessibility > 0:
            for i in range(1, persons_needing_accessibility + 1):
                selections = request.POST.getlist(f'accessibilities_person_{i}')
                if selections:
                    accessibility_selections_per_person.append(selections)

        base_amount, acc_amount, total_amount = calculate_booking_amount(
            tour,
            total_persons,
            accessibility_selections_per_person
        )
        booking = Booking()
        booking.traveller = traveller
        booking.tour = tour
        booking.tour_date = tour_date
        booking.total_persons = total_persons
        booking.persons_needing_accessibility = persons_needing_accessibility
        booking.caregiver_gender_preference = caregiver_gender
        booking.base_amount = base_amount
        booking.accessibility_amount = acc_amount
        booking.total_amount = total_amount
        booking.commission_amount = total_amount * 0.10  # 10% Commission
        booking.save()

        # Save selected accessibilities per person (one record per person-accessibility pair)
        for person_selections in accessibility_selections_per_person:
            for acc in person_selections:
                booking_acc = BookingAccessibility()
                booking_acc.booking = booking
                booking_acc.accessibility = Accessibility.objects.get(accessibility_id=acc)
                booking_acc.save()
        
        # Redirect to booking success page
        return redirect('booking_success', booking_id=booking.booking_id)

def booking_success(request, booking_id):
    """Display the booking success page"""
    return render(request, 'traveller/booking_success.html')

def payment(request, booking_id):
    """Display the payment page for a booking"""
    try:
        booking = Booking.objects.get(booking_id=booking_id)
    except Booking.DoesNotExist:
        return HttpResponse("<script>alert('Booking not found.');window.location.href='/tour-packages/';</script>")
    
    return render(request, 'traveller/payment.html', {'booking': booking})

def process_payment(request, booking_id):
    """Process the payment for a booking"""
    if request.method == 'POST':
        try:
            booking = Booking.objects.get(booking_id=booking_id)
        except Booking.DoesNotExist:
            return HttpResponse("<script>alert('Booking not found.');window.location.href='/tour-packages/';</script>")
        
        payment_method = request.POST.get('payment_method')
        
        # Create Payment record

        transaction_id = str(uuid.uuid4())
        
        payment = Payment.objects.create(
            booking=booking,
            payment_method=payment_method,
            transaction_id=transaction_id,
            amount=booking.total_amount,
            payment_status='success'
        )

        # Update booking status to confirmed/paid
        booking.booking_status = 'paid'
        booking.save()
        
        return HttpResponse("<script>alert('Payment successful! Your booking is confirmed.');window.location.href='/tour-packages/';</script>")
    
    return HttpResponse("<script>alert('Invalid request.');window.location.href='/tour-packages/';</script>")    

def profile_view(request):
    login_id = request.session.get('login_id')
    if not login_id:
        return HttpResponse("<script>alert('Please login to view your profile.'); window.location.href='/login/';</script>")
    
    try:
        traveller = TravellerProfile.objects.get(login=login_id)
    except TravellerProfile.DoesNotExist:
        # Fallback or error handling
        return HttpResponse("<script>alert('Profile not found.'); window.location.href='/login/';</script>")
        
    return render(request, 'traveller/profile_view.html', {'traveller': traveller})

def change_password(request):
    login_id = request.session.get('login_id')
    if not login_id:
        return HttpResponse("<script>alert('Please login first.'); window.location.href='/login/';</script>")

    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        try:
            user_login = login.objects.get(login_id=login_id)
            
            if user_login.password != current_password:
                 return HttpResponse("<script>alert('Incorrect current password.'); window.history.back();</script>")
            
            if new_password != confirm_password:
                return HttpResponse("<script>alert('New passwords do not match.'); window.history.back();</script>")
                
            if len(new_password) < 8:
                 return HttpResponse("<script>alert('Password must be at least 8 characters long.'); window.history.back();</script>")

            user_login.password = new_password
            user_login.save()
            
            return HttpResponse("<script>alert('Password updated successfully!'); window.location.href='/profile/';</script>")
            
        except login.DoesNotExist:
             return HttpResponse("<script>alert('User not found.'); window.location.href='/login/';</script>")

    return render(request, 'traveller/change_password.html')

def edit_profile(request):
    login_id = request.session.get('login_id')
    if not login_id:
        return HttpResponse("<script>alert('Please login first.'); window.location.href='/login/';</script>")

    try:
        traveller = TravellerProfile.objects.get(login=login_id)
    except TravellerProfile.DoesNotExist:
        return HttpResponse("<script>alert('Profile not found.'); window.location.href='/login/';</script>")

    if request.method == 'POST':
        traveller.traveller_name = request.POST.get('name')
        traveller.phone = request.POST.get('phone')
        traveller.address = request.POST.get('address')
        traveller.city = request.POST.get('city')
        traveller.pincode = request.POST.get('pincode')
        
        district_id = request.POST.get('district')
        if district_id:
            traveller.district = District.objects.get(district_id=district_id)
        
        # Email update - check for uniqueness if changed
        new_email = request.POST.get('email')
        if new_email != traveller.email:
            if TravellerProfile.objects.filter(email=new_email).exists():
                return HttpResponse(f"<script>alert('Email {new_email} is already in use.'); window.history.back();</script>")
            traveller.email = new_email

        traveller.save()
        return HttpResponse("<script>alert('Profile updated successfully!'); window.location.href='/profile/';</script>")

    districts = District.objects.all()
    return render(request, 'traveller/edit_profile.html', {'traveller': traveller, 'districts': districts})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def my_bookings(request):
    login_id = request.session.get('login_id')
    if not login_id:
        return redirect('login')
    
    try:
        traveller = TravellerProfile.objects.get(login_id=login_id)
        # Order by pending first, then by date descending
        bookings = Booking.objects.filter(traveller=traveller).annotate(
            status_priority=Case(
                When(booking_status='pending', then=Value(1)),
                default=Value(2),
                output_field=IntegerField(),
            )
        ).order_by('status_priority', '-booking_date')
        
        # Attach first image for each booking's tour
        for booking in bookings:
            image_obj = TourImages.objects.filter(tour=booking.tour).first()
            if image_obj:
                booking.tour_image_url = image_obj.image.url
            else:
                booking.tour_image_url = None
                
    except TravellerProfile.DoesNotExist:
         return HttpResponse("<script>alert('Profile not found.'); window.location.href='/login/';</script>")
         
    return render(request, 'traveller/bookings_view.html', {'bookings': bookings})
