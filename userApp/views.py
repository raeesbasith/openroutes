from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_control
from adminApp.models import District, Location, Accessibility
from operatorApp.models import Tour, TourAccessibility, TourImages
from userApp.models import *
from guestApp.models import *
import uuid
from django.db.models import Case, When, Value, IntegerField, Count, Avg
from datetime import datetime
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import smtplib
from email.message import EmailMessage

# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def traveller_home(request):
    if request.session.get('login_id'):
        login_id = request.session['login_id']
        traveller = get_object_or_404(TravellerProfile, login_id=login_id)
        
        # Base Query: Available tours (not limited to only traveller's district anymore)
        recommended_tours = Tour.objects.filter(status='available')
        
        # Filter by Traveller's Accessibility Needs (Must match at least one)
        needed_access_ids = list(TravellerAccessibility.objects.filter(traveller=traveller).values_list('accessibility_id', flat=True))
        
        if needed_access_ids:
            # Filter for tours that have AT LEAST ONE of the needed accessibilities
            # We use filter(field__in=list) for OR matching logic
            recommended_tours = recommended_tours.filter(touraccessibility__accessibility_id__in=needed_access_ids).distinct()
        
        # Annotate and Sort:
        # 1. District Priority: Same district first
        # 2. Review Count: More reviews first (Descending)
        # 3. Average Rating: Higher rating first (Descending)
        recommended_tours = recommended_tours.annotate(
            district_priority=Case(
                When(location__district=traveller.district, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            ),
            review_count=Count('review', distinct=True),
            avg_rating=Avg('review__rating')
        ).order_by('-district_priority', '-review_count', '-avg_rating')[:6] # Top 6 recommendations
        
        context = {
            'recommended_tours': recommended_tours
        }
        return render(request, 'traveller/traveller_home.html', context)
    else:
        return redirect('login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def tour_packages_view(request):
    if not request.session.get('login_id'):
        return redirect('login')
    
    Districts = District.objects.all()
    accessibilities = Accessibility.objects.all()
    # Base queryset with average rating annotation
    Tour_list = Tour.objects.all().annotate(
        avg_rating=Avg('review__rating')
    ).order_by('price')

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


def tour_detail(request, tour_id):
    tour = get_object_or_404(Tour, tour_id=tour_id)
    reviews = Review.objects.filter(tour=tour).order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    return render(request, 'traveller/tour_detail.html', {
        'tour': tour, 
        'reviews': reviews, 
        'avg_rating': avg_rating
    })

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

        # Validate that tour_date is not in the past or today
        try:
             tour_date_obj = datetime.strptime(tour_date, '%Y-%m-%d').date()
             if tour_date_obj <= timezone.now().date():
                  return HttpResponse("<script>alert('Error: You cannot book a tour for today or a past date. Please select a future date.');window.history.back();</script>")
        except ValueError:
             return HttpResponse("<script>alert('Error: Invalid date format.');window.history.back();</script>")

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

def submit_review(request, booking_id):
    login_id = request.session.get('login_id')
    if not login_id:
        return HttpResponse("<script>alert('Please login first.'); window.location.href='/login/';</script>")

    if request.method == 'POST':
        try:
            booking = Booking.objects.get(booking_id=booking_id)
            if booking.traveller.login_id != login_id:
                return HttpResponse("<script>alert('Unauthorized access.'); window.location.href='/my-bookings/';</script>")
            
            if hasattr(booking, 'review'):
                 return HttpResponse("<script>alert('You have already reviewed this booking.'); window.location.href='/my-bookings/';</script>")

            rating = request.POST.get('rating')
            comment = request.POST.get('comment')

            Review.objects.create(
                booking=booking,
                tour=booking.tour,
                traveller=booking.traveller,
                rating=rating,
                comment=comment
            )
            return HttpResponse("<script>alert('Review submitted successfully!'); window.location.href='/my-bookings/';</script>")
        
        except Booking.DoesNotExist:
             return HttpResponse("<script>alert('Booking not found.'); window.location.href='/my-bookings/';</script>")
    
    return redirect('my_bookings')

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

        # Send Payment Confirmation & Invoice Email
        try:
            traveller_email = booking.traveller.email
            subject = "Payment Receipt & Invoice - OpenRoutes"
            
            invoice_html = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="border: 1px solid #ccc; padding: 20px; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #4CAF50;">Payment Successful</h2>
                    <p>Dear {booking.traveller.traveller_name},</p>
                    <p>Thank you for your payment. Your booking is now confirmed.</p>
                    
                    <hr>
                    <h3>Invoice Details</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Invoice No:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;">INV-{booking.booking_id}-{transaction_id[:8]}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Transaction ID:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{transaction_id}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Date:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{timezone.now().strftime('%Y-%m-%d %H:%M')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Tour Package:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{booking.tour.tour_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Total Amount Paid:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>₹{booking.total_amount}</strong></td>
                        </tr>
                    </table>
                    
                    <p style="margin-top: 20px;">You can view your booking details at any time from your account.</p>
                    
                    <p>Happy Travels!<br>OpenRoutes Team</p>
                </div>
            </body>
            </html>
            """
            
            msg = EmailMessage()
            msg.set_content("Thank you for your payment. Please find your invoice details below.") # Fallback text
            msg.add_alternative(invoice_html, subtype='html')
            
            msg['Subject'] = subject
            msg['From'] = 'raeesbasith15@gmail.com'
            msg['To'] = traveller_email

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(
                    'raeesbasith15@gmail.com',
                    'qfac dtcm rsbb pwyg'
                )
                smtp.send_message(msg)
                
            print(f"Invoice email sent to {traveller_email}")
            
        except Exception as e:
            print(f"Error sending invoice email: {e}")
        
        return HttpResponse("<script>alert('Payment successful! Your booking is confirmed.');window.location.href='/my-bookings/';</script>")
    
    return HttpResponse("<script>alert('Invalid request.');window.location.href='/tour-packages/';</script>")    

def cancel_booking(request, booking_id):
    login_id = request.session.get('login_id')
    if not login_id:
        return redirect('login')
    if request.method != 'POST':
        return redirect('my_bookings')

    booking = get_object_or_404(Booking, booking_id=booking_id, traveller__login_id=login_id)

    if booking.booking_status != 'pending':
        return HttpResponse("<script>alert('Only pending bookings can be cancelled directly. For confirmed bookings, please request cancellation.'); window.location.href='/my-bookings/';</script>")

    cancellation_reason = request.POST.get('cancellation_reason', '').strip()
    booking.booking_status = 'cancelled'
    booking.cancellation_reason = cancellation_reason if cancellation_reason else None
    booking.cancellation_requested_at = timezone.now()
    booking.save()

    return HttpResponse("<script>alert('Booking cancelled successfully.'); window.location.href='/my-bookings/';</script>")

def request_cancellation(request, booking_id):
    login_id = request.session.get('login_id')
    if not login_id:
        return redirect('login')
    if request.method != 'POST':
        return redirect('my_bookings')

    booking = get_object_or_404(Booking, booking_id=booking_id, traveller__login_id=login_id)

    if booking.booking_status not in ['paid', 'confirmed']:
        return HttpResponse("<script>alert('Only confirmed or paid bookings can request cancellation.'); window.location.href='/my-bookings/';</script>")

    cancellation_reason = request.POST.get('cancellation_reason', '').strip()
    if not cancellation_reason:
        return HttpResponse("<script>alert('Please provide a reason for cancellation.'); window.history.back();</script>")

    booking.booking_status = 'cancel_requested'
    booking.cancellation_reason = cancellation_reason
    booking.cancellation_requested_at = timezone.now()
    booking.save()

    return HttpResponse("<script>alert('Cancellation request submitted. Operator will review it shortly.'); window.location.href='/my-bookings/';</script>")

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
            
        # Update Accessibility Preferences
        selected_accessibilities = request.POST.getlist('accessibility')
        # Clear existing preferences
        TravellerAccessibility.objects.filter(traveller=traveller).delete()
        # Add new preferences
        for acc_id in selected_accessibilities:
            try:
                acc = Accessibility.objects.get(accessibility_id=acc_id)
                TravellerAccessibility.objects.create(traveller=traveller, accessibility=acc)
            except Accessibility.DoesNotExist:
                continue
        
        # Email update - check for uniqueness if changed
        new_email = request.POST.get('email')
        if new_email != traveller.email:
            if TravellerProfile.objects.filter(email=new_email).exists():
                return HttpResponse(f"<script>alert('Email {new_email} is already in use.'); window.history.back();</script>")
            traveller.email = new_email

        traveller.save()
        return HttpResponse("<script>alert('Profile updated successfully!'); window.location.href='/profile/';</script>")

    districts = District.objects.all()
    accessibilities = Accessibility.objects.all()
    # Get current selections to pre-fill checkboxes
    current_accessibilities = TravellerAccessibility.objects.filter(traveller=traveller).values_list('accessibility_id', flat=True)
    
    return render(request, 'traveller/edit_profile.html', {
        'traveller': traveller, 
        'districts': districts,
        'accessibilities': accessibilities,
        'current_accessibilities': current_accessibilities
    })

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def my_bookings(request):
    login_id = request.session.get('login_id')
    if not login_id:
        return redirect('login')
    
    try:
        traveller = TravellerProfile.objects.get(login_id=login_id)
        # Prioritize actionable items first
        bookings = Booking.objects.filter(traveller=traveller).annotate(
            status_priority=Case(
                When(booking_status='cancellation_requested', then=Value(0)),
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
            
            try:
                booking.has_review = booking.review is not None
                booking.user_rating = booking.review.rating
            except Review.DoesNotExist:
                booking.has_review = False
                
    except TravellerProfile.DoesNotExist:
         return HttpResponse("<script>alert('Profile not found.'); window.location.href='/login/';</script>")
         
    return render(request, 'traveller/bookings_view.html', {'bookings': bookings})

def delete_traveller_account(request):
    if not request.session.get('login_id'):
        return redirect('login')
    
    login_id = request.session['login_id']
    try:
        user_login = login.objects.get(login_id=login_id)
        user_login.delete()
        request.session.flush()
        return HttpResponse("<script>alert('Your account has been deleted successfully.'); window.location.href='/';</script>")
    except Exception as e:
        return HttpResponse(f"<script>alert('Error: {str(e)}'); window.history.back();</script>")
