from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """Extends Django's built-in User with extra fields from the PDF."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    contact_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


class Address(models.Model):
    """Users can add addresses as per the Settings requirement."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.username} - {self.city}"


class Attempt(models.Model):
    """Stores every Armstrong check/range search a user makes."""

    MODE_CHOICES = [
        ('single', 'Single Number Check'),
        ('range', 'Range Search'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attempts')
    mode = models.CharField(max_length=10, choices=MODE_CHOICES)

    input_number = models.BigIntegerField(null=True, blank=True)
    is_armstrong = models.BooleanField(null=True, blank=True)

    range_min = models.BigIntegerField(null=True, blank=True)
    range_max = models.BigIntegerField(null=True, blank=True)
    armstrong_numbers_found = models.JSONField(default=list)  # e.g. [1, 153, 370]
    count_found = models.IntegerField(default=0)

    attempted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} | {self.mode} | {self.attempted_at}"


class Feedback(models.Model):
    """Submit Feedback requirement from the PDF."""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='feedbacks')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.name}"
