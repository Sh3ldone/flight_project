from django.shortcuts import render, get_object_or_404, redirect
from .forms import AdminFlightReservationForm, UserFlightReservationForm, FlightScheduleForm, UserRegisterForm
from django.contrib import messages
from .models import FlightReservation, FlightSchedule
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.views import LoginView
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from .serializers import FlightReservationSerializer, FlightScheduleSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import logout as django_logout
from django.db import transaction
from django.urls import reverse
from .forms import SupportForm
from django.core.mail import send_mail, EmailMultiAlternatives # Make sure this import is at the top
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import Http404
from django.http import HttpResponse
from django.contrib.auth.models import User
 
 

 

def create_superuser(request):
    if User.objects.filter(is_superuser=True).exists():
        return HttpResponse("Superuser already exists.")
    else:
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        return HttpResponse("Superuser created: username='admin', password='admin123'")
 
# Admin Dashboard View

@login_required
@staff_member_required
def admin_dashboard(request):
    reservations = FlightReservation.objects.filter(status='active')
    past_reservations = FlightReservation.objects.exclude(status='active')

    context = {
        'flight_schedules': FlightSchedule.objects.all(),
        'reservations': reservations,
        'past_reservations': past_reservations,
    }
    return render(request, 'reservations/admin_dashboard.html', context)



@login_required
@staff_member_required
def edit_flight_schedule(request, pk):
    schedule = get_object_or_404(FlightSchedule, pk=pk)
    flight_numbers = ["A4351", "A5644", "A3009", "B2345"]  # Pass this list to template

    if request.method == 'POST':
        form = FlightScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Flight schedule updated successfully!')
            return redirect('edit_flight_schedule', pk=pk)  # PRG pattern
        else:
            messages.error(request, 'Error updating flight schedule: ' + str(form.errors))
    else:
        form = FlightScheduleForm(instance=schedule)

    context = {
        'form': form,
        'schedule': schedule,
        'flight_numbers': flight_numbers,
    }
    return render(request, 'reservations/edit_flight_schedule.html', context)



def edit_schedule(request, id):  # <-- Accept the id parameter
    schedule = get_object_or_404(FlightSchedule, pk=id)
    
    if request.method == 'POST':
        form = FlightScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')  # or wherever you want to go after editing
    else:
        form = FlightScheduleForm(instance=schedule)
    
    return render(request, 'reservations/edit_schedules.html', {'form': form, 'schedule': schedule})

# Home Page
def home(request):
    flight_schedules = FlightSchedule.objects.all()
    return render(request, 'reservations/home.html', {
        'flight_schedules': flight_schedules
    })

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # use .get() to avoid crash
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'Both fields are required.')
            return render(request, 'reservations/login.html')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            else:
                return redirect('user_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'reservations/login.html')

# Login Page for admin
#def login_user(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')  # Redirect to select-role if already logged in
    return LoginView.as_view(template_name='reservations/login.html')(request)  # Show login page if not authenticated



def login_users(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user is NOT staff/admin
            if not user.is_staff:
                login(request, user)
                return redirect('user_dashboard')
            else:
                messages.error(request, "This login page is for regular users only.")
        else:
            messages.error(request, "Invalid credentials.")
    
    return render(request, 'reservations/login_user.html') 

# View Flight Schedule for User
def view_flight_schedule(request):
    # Filter flights with available seats > 0
    flight_schedules = FlightSchedule.objects.filter(available_seats__gt=0).order_by('departure_time')
    
    context = {
        'flight_schedules': flight_schedules
    }
    return render(request, 'reservations/view_flight_schedule.html', context)


def view_flight_schedule1(request):
    schedules = FlightSchedule.objects.all()
    return render(request, 'reservations/view_flight_schedule1.html', {'schedules': schedules})

# Book a Flight

@login_required
@transaction.atomic
def book_a_flight(request, flight_id):
    # Lock the row to prevent race condition on available_seats
    flight_schedule = get_object_or_404(FlightSchedule.objects.select_for_update(), id=flight_id)

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        seats_booked_str = request.POST.get('seats_booked', '0')

        try:
            seats_booked = int(seats_booked_str)
        except ValueError:
            seats_booked = 0

        if seats_booked <= 0:
            messages.error(request, 'Please enter a valid number of seats.')
        elif seats_booked > flight_schedule.available_seats:
            messages.error(request, 'Not enough available seats!')
        else:
            # Redirect to payment page passing details via URL query parameters
            payment_url = (
                f"{reverse('payment', args=[flight_id])}"
                f"?full_name={full_name}&email={email}&seats_booked={seats_booked}"
            )
            return redirect(payment_url)

    return render(request, 'reservations/book_a_flight.html', {
        'flight_schedule': flight_schedule,
    })
    
# Admin List of Reservations
@login_required
def list_reservations(request):
    if request.user.is_staff:
        reservations = FlightReservation.objects.select_related('flight_schedule').all()
    else:
        # Show only active reservations for users
        reservations = FlightReservation.objects.select_related('flight_schedule').filter(user=request.user, status='active')
    return render(request, 'reservations/list_reservations.html', {'reservations': reservations})


# Edit a Reservation
@login_required
def edit_reservation(request, reservation_id):
    reservation = get_object_or_404(FlightReservation, id=reservation_id)

    # Choose form class based on user type
    if request.user.is_staff:
        form_class = AdminFlightReservationForm
    else:
        # Only allow editing if this reservation belongs to the user
        if reservation.user != request.user:
            messages.error(request, "You don't have permission to edit this reservation.")
            return redirect('list_reservations')
        form_class = UserFlightReservationForm

    if request.method == 'POST':
        form = form_class(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            messages.success(request, "Reservation updated successfully.")
            
            # Redirect based on user type
            if request.user.is_staff:
                return redirect('admin_dashboard')
            else:
                return redirect('user_dashboard')  # or 'list_reservations' if that is the user page
    else:
        form = form_class(instance=reservation)

    return render(request, 'reservations/edit_reservation.html', {
        'form': form,
        'reservation': reservation,
    })
# Cancel a Reservation


@login_required
@transaction.atomic
def cancel_reservation(request, reservation_id):
    try:
        if request.user.is_staff:
            reservation = FlightReservation.objects.get(id=reservation_id)
        else:
            reservation = FlightReservation.objects.get(id=reservation_id, user=request.user)
    except FlightReservation.DoesNotExist:
        raise Http404("No FlightReservation matches the given query.")

    if reservation.status != 'canceled':
        flight = reservation.flight_schedule
        flight.available_seats += reservation.seats_booked
        flight.save()

        reservation.status = 'canceled'
        reservation.save()
    
    messages.success(request, "Reservation canceled and seats freed.")
    return redirect('user_dashboard' if not request.user.is_staff else 'admin_dashboard')


# Admin Add Flight Schedule
@login_required
@staff_member_required
def add_flight_schedule(request):
    if request.method == 'POST':
        form = FlightScheduleForm(request.POST)
        if form.is_valid():
            form.save()  # <--- price might be treated as string or not cast properly here
            messages.success(request, 'Flight schedule added successfully!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FlightScheduleForm()

    return render(request, 'reservations/add_flight_schedule.html', {'form': form})
 

# Admin Delete Flight Schedule
@login_required
@staff_member_required
def delete_flight_schedule(request, id):
    schedule = get_object_or_404(FlightSchedule, pk=id)
    schedule.delete()
    messages.success(request, "Flight schedule deleted successfully.")
    return redirect('admin_dashboard')  # or wherever your dashboard URL name is

# Redirect User Based on Role
def select_role(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')  # Redirect to Admin Dashboard
        else:
            return redirect('home')  # Redirect to User's Home page or flight schedule
    return redirect('login')  # If not authenticated, redirect to login page

#user registration

def register_user(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created. You can now log in.')
            return redirect('login_users')  # or 'login_user' depending on your setup
    else:
        form = UserRegisterForm()

    return render(request, 'reservations/register.html', {'form': form})

#User dashboard
def user_dashboard(request):
    flight_schedules = FlightSchedule.objects.all()
    return render(request, 'reservations/user_dashboard.html', {
        'flight_schedules': flight_schedules
    })
     

#logout
def logout_view(request):
    logout(request)
    return redirect('login_users')



#booking
def booking_flight(request):
    # Basic query: all flight schedules with available seats > 0
    flight_schedules = FlightSchedule.objects.filter(available_seats__gt=0)

    # Optional: filter based on search query params
    origin = request.GET.get('from')
    destination = request.GET.get('to')
    depart_date = request.GET.get('depart')

    if origin:
        flight_schedules = flight_schedules.filter(origin__icontains=origin)
    if destination:
        flight_schedules = flight_schedules.filter(destination__icontains=destination)
    if depart_date:
        flight_schedules = flight_schedules.filter(departure_date=depart_date)

    context = {
        'flight_schedules': flight_schedules
    }
    return render(request, 'reservations/booking.html', context)



@login_required
@transaction.atomic  # Important para atomic transaction
def payment(request, flight_id):
    flight_schedule = get_object_or_404(FlightSchedule.objects.select_for_update(), id=flight_id)

    # Get seats_booked from GET or POST:
    if request.method == 'GET':
        try:
            seats_booked = int(request.GET.get('seats_booked', 1))
        except (ValueError, TypeError):
            seats_booked = 1
    else:
        # On POST, seats_booked should come hidden or from POST data
        try:
            seats_booked = int(request.POST.get('seats_booked', 1))
        except (ValueError, TypeError):
            seats_booked = 1

    # Validate seats_booked:
    if seats_booked < 1:
        messages.error(request, "Invalid number of seats.")
        return redirect('book_a_flight', flight_id=flight_id)
    if seats_booked > flight_schedule.available_seats:
        messages.error(request, "Not enough available seats.")
        return redirect('book_a_flight', flight_id=flight_id)

    total_price = flight_schedule.price * seats_booked

    if request.method == 'POST':
        cardholder = request.POST.get('cardholder')
        cardnumber = request.POST.get('cardnumber')
        expiry = request.POST.get('expiry')
        cvv = request.POST.get('cvv')
        email = request.POST.get('email')

        # Simulate payment success here
        payment_success = True

        if payment_success:
            # Create reservation
            FlightReservation.objects.create(
                flight_schedule=flight_schedule,
                full_name=cardholder,
                email=email,
                seats_booked=seats_booked,
                user=request.user,
            )
            
            # Deduct seats atomically
            flight_schedule.available_seats -= seats_booked
            if flight_schedule.available_seats < 0:
                messages.error(request, "Seats are no longer available.")
                return redirect('book_a_flight', flight_id=flight_id)
            flight_schedule.save()

            # Send confirmation email
            subject = 'Flight Booking Confirmation'
            html_content = render_to_string('emails/flight_reservation_confirmation.html', {
                'full_name': cardholder,
                'flight_schedule': flight_schedule,
                'seats_booked': seats_booked,
                'total_price': total_price,
            })
            text_content = strip_tags(html_content)

            email_message = EmailMultiAlternatives(subject, text_content, None, [email])
            email_message.attach_alternative(html_content, "text/html")
            email_message.send()

            messages.success(request, "Payment successful! Your flight is booked. Confirmation email sent.")
            return redirect('user_dashboard')
        else:
            messages.error(request, "Payment failed. Please try again.")

    context = {
        'flight_schedule': flight_schedule,
        'seats_booked': seats_booked,
        'total_price': total_price,
    }
    return render(request, 'reservations/payment.html', context)

def contact_support(request):
    if request.method == 'POST':
        form = SupportForm(request.POST)
        if form.is_valid():
            # Send email (configure email backend in settings.py first)
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            full_message = f"From: {name} <{email}>\n\n{message}"

            send_mail(
    subject,
    full_message,
    'sheldonedacuya91@gmail.com',  # from email - must be allowed by your SMTP
    ['sheldonedacuya2004@gmail.com'],  # to email - where you receive support messages
    fail_silently=False,
)

            messages.success(request, "Your message has been sent! We'll get back to you soon.")
            return redirect('contact_support')
    else:
        form = SupportForm()
    return render(request, 'support/contact.html', {'form': form})


#API
class FlightScheduleViewSet(viewsets.ModelViewSet):
    queryset = FlightSchedule.objects.all()
    serializer_class = FlightScheduleSerializer
    permission_classes = [IsAuthenticated]

class FlightReservationViewSet(viewsets.ModelViewSet):
    queryset = FlightReservation.objects.all()
    serializer_class = FlightReservationSerializer
    permission_classes = [IsAuthenticated]






    
