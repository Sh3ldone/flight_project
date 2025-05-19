from django import forms
from .models import FlightReservation, FlightSchedule
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# Admin Reservation Form — full editable fields
class AdminFlightReservationForm(forms.ModelForm):
    flight_schedule = forms.ModelChoiceField(
        queryset=FlightSchedule.objects.all(),
        label="Flight Schedule"
    )

    class Meta:
        model = FlightReservation
        fields = ['full_name', 'email', 'flight_schedule', 'seats_booked']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'flight_schedule'):
            self.fields['flight_schedule'].initial = self.instance.flight_schedule


# User Reservation Form — limited fields only
class UserFlightReservationForm(forms.ModelForm):
    class Meta:
        model = FlightReservation
        fields = ['full_name', 'email']


# Flight Schedule Form (unchanged)
class FlightScheduleForm(forms.ModelForm):
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        label='Price (₱)',
        widget=forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'e.g. 1999.99'})
    )

    class Meta:
        model = FlightSchedule
        fields = ['flight_number', 'origin', 'destination', 'departure_date', 'departure_time', 'available_seats', 'price']
        widgets = {
            'departure_date': forms.DateInput(attrs={'type': 'date'}),
            'departure_time': forms.TimeInput(attrs={'type': 'time'}),
        }


# User registration form (unchanged)
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class SupportForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=200)
    message = forms.CharField(widget=forms.Textarea)
