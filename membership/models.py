from django.db import models
from django.utils import timezone
import random
import string


class Member(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    MEMBERSHIP_CATEGORIES = [
        ('Ordinary Membership', 'Ordinary Membership'),
        ('Bronze Membership', 'Bronze Membership'),
        ('Life Membership', 'Life Membership'),
        ('Associate Membership', 'Associate Membership'),
        ('Group Membership', 'Group Membership'),
        ('Honorary Membership', 'Honorary Membership'),
    ]

    # Personal Information
    surname = models.CharField(max_length=100)
    other_names = models.CharField(max_length=200)
    id_passport = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    ethnicity = models.CharField(max_length=100, blank=True)
    religion = models.CharField(max_length=100, blank=True)
    dob = models.DateField()

    # Special Interest Groups (stored as JSON)
    special_interest = models.JSONField(default=list, blank=True)
    pwd_number = models.CharField(max_length=50, blank=True, null=True)

    # Location
    county = models.CharField(max_length=100)
    constituency = models.CharField(max_length=100)
    ward = models.CharField(max_length=100, blank=True)
    polling_station = models.CharField(max_length=200, blank=True)

    # Membership
    membership_category = models.CharField(max_length=50, choices=MEMBERSHIP_CATEGORIES)
    membership_number = models.CharField(max_length=20, unique=True, blank=True)
    registration_date = models.DateTimeField(default=timezone.now)

    # Verification
    phone_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)

    # Certificate
    certificate_generated = models.BooleanField(default=False)
    certificate_file = models.FileField(upload_to='certificates/', blank=True, null=True)
    certificate_sent = models.BooleanField(default=False)

    # Status
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-registration_date']
        verbose_name = 'Member'
        verbose_name_plural = 'Members'
        indexes = [
            models.Index(fields=['membership_number']),
            models.Index(fields=['id_passport']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.surname} {self.other_names} - {self.membership_number}"

    def save(self, *args, **kwargs):
        if not self.membership_number:
            self.membership_number = self.generate_membership_number()
        super().save(*args, **kwargs)

    def generate_membership_number(self):
        prefix = 'NPV'
        year = timezone.now().year
        random_part = ''.join(random.choices(string.digits, k=6))
        membership_num = f"{prefix}{year}{random_part}"

        # Ensure uniqueness
        while Member.objects.filter(membership_number=membership_num).exists():
            random_part = ''.join(random.choices(string.digits, k=6))
            membership_num = f"{prefix}{year}{random_part}"

        return membership_num

    def get_full_name(self):
        return f"{self.surname} {self.other_names}"

    def get_age(self):
        today = timezone.now().date()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

