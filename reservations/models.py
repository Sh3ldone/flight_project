from django.db import models
from django.contrib.auth.models import User

class FlightSchedule(models.Model):
    flight_number = models.CharField(max_length=10)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_date = models.DateField()
    departure_time = models.TimeField()
    available_seats = models.IntegerField(default=0)
    price = models.IntegerField()

    def __str__(self):
        return f"Flight {self.flight_number} from {self.origin} to {self.destination} on {self.departure_date}"

class FlightReservation(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('canceled', 'Canceled'),
    ]

    flight_schedule = models.ForeignKey(
        FlightSchedule,
        on_delete=models.SET_NULL,      # Keeps reservation even if schedule is deleted
        related_name='reservations',
        null=True,                      # Allows NULL after deletion
        blank=True
    )
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    seats_booked = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        # Handle deleted schedule gracefully
        schedule_info = (
            f"{self.flight_schedule.origin} to {self.flight_schedule.destination}"
            if self.flight_schedule else "Schedule deleted"
        )
        return f"{self.full_name} - {schedule_info} ({self.status})"