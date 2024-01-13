from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from django.db.models.signals import pre_save
from django.dispatch import receiver


class ReaderManager(BaseUserManager):
    """
    Custom manager for the Reader model.

    This manager provides methods for creating regular users and superusers with specific attributes.

    Methods:
        - create_user(email, password, **extra_fields): Creates a regular user with the given email and password.
        - create_superuser(email, password, **extra_fields): Creates a superuser with additional staff and superuser attributes.

    Example Usage:
    manager = ReaderManager()
    user = manager.create_user('user@example.com', 'password123')
    superuser = manager.create_superuser('admin@example.com', 'adminpassword')

    Note:
        - The create_user method sets a normalized email, sets the password, and saves the user to the database.
        - The create_superuser method sets additional attributes for a superuser, such as is_staff and is_superuser.
    """

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('email_is_verified', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class Reader(AbstractUser):
    """
    Custom user model representing a reader in the system.

    This model extends Django's AbstractUser to customize user attributes and behavior.

    Attributes:
        - balance (DecimalField): Field representing the user's balance with default value 0.00.
        - email (EmailField): Field representing the user's email address with unique constraint.
        - email_is_verified (BooleanField): Field indicating whether the user's email address has been verified.

    Fields:
        - USERNAME_FIELD (str): Specifies the field used for authentication (email in this case).
        - REQUIRED_FIELDS (list): List of required fields for creating a user.

    Manager:
        - objects (ReaderManager): Custom manager for handling Reader model instances.

    Methods:
        - __str__(): Returns a string representation of the user (email).
        - save(*args, **kwargs): Custom save method to perform additional actions when saving the user.

    Example Usage:
    reader = Reader.objects.create_user('user@example.com', 'password123')
    print(reader.balance)  # Accessing the user's balance field.

    Note:
        - The Reader model uses email as the unique identifier for authentication.
        - The custom save method can be extended for additional logic when saving the user.
    """
    balance = models.DecimalField(default=0.00,
                                  decimal_places=2,
                                  max_digits=10)
    username = None
    email = models.EmailField(_('Email Address'), max_length=50, unique=True)
    email_is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = ReaderManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def update_balance(self):
        late_books = CheckedOutBook.objects.all().filter(reader=self, is_counted=False)
        total_penalty = Decimal(str(0))
        for book in late_books:
            total_penalty += Decimal(str(book.calculate_penalty()))
        self.balance += total_penalty
        late_books.update(is_counted=True)
        self.save()


class Reservation(models.Model):
    """
    Model representing a reservation made by a reader for a book in the system.

    Attributes:
        - reader (ForeignKey): Relation to the Reader model representing the user who made the reservation.
        - book (ForeignKey): Relation to the Book model representing the reserved book.
        - start_date (DateTimeField): Field representing the start date and time of the reservation.
        - end_date (DateTimeField): Field representing the end date and time of the reservation.
        - is_active (BooleanField): Field indicating whether the reservation is currently active.
        - should_remind (BooleanField): Field indicating whether a reminder should be sent for the reservation.
        - add_info (TextField): Field for additional information related to the reservation (optional).

    Methods:
        - end_reservation(): Method to end the reservation, updating related fields and saving changes.

    Example Usage:
    reservation = Reservation.objects.get(pk=1)
    reservation.end_reservation()  # Ending an active reservation.

    Note:
        - The end_reservation method checks if the reservation end date is in the past and updates relevant fields.
        - is_active is set to False, and the book's availability is restored when the reservation ends.
    """
    reader = models.ForeignKey('Reader', on_delete=models.CASCADE)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    should_remind = models.BooleanField(default=True)
    add_info = models.TextField(null=True, blank=True)

    def end_reservation(self):
        """
        End the reservation, updating relevant fields and saving changes.

        If the end date of the reservation is in the past, set is_active to False,
        mark the associated book as available, and save the changes.
        """
        if self.end_date < timezone.now().date():
            self.is_active = False
            self.book.is_available = True
            self.save()
            self.book.save()


class CheckedOutBook(models.Model):
    """
    Model representing a book checked out by a reader in the system.

    Attributes:
        - reader (ForeignKey): Relation to the Reader model representing the user who checked out the book.
        - book (ForeignKey): Relation to the Book model representing the checked-out book.
        - start_date (DateField): Field representing the date when the book was checked out.
        - due_date (DateField): Field representing the due date for returning the book.
        - end_date (DateField): Field representing the date when the book was returned (optional).

    Methods:
        - calculate_penalty(): Method to calculate a penalty fee based on the delay in returning the book.

    Example Usage:
    checked_out_book = CheckedOutBook.objects.get(pk=1)
    penalty_fee = checked_out_book.calculate_penalty()  # Calculating penalty if the book is returned late.

    Note:
        - The calculate_penalty method determines if the book was returned late and calculates a penalty fee.
        - The penalty fee is calculated based on a fixed rate for each day the book is overdue.
    """
    reader = models.ForeignKey('Reader', on_delete=models.CASCADE)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    start_date = models.DateField()
    due_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_penalty_paid = models.BooleanField(default=False)
    is_counted = models.BooleanField(default=False)

    def calculate_penalty(self):
        """
        Calculate a penalty fee based on the delay in returning the book.

        If the book is returned late, calculate the penalty fee based on the number of days overdue.
        Penalty is calculated at a fixed rate of 2.00 units per day.

        :return: penalty_fee (float): The calculated penalty fee.
        """
        if self.end_date and self.end_date > self.due_date:
            days_delayed = (self.end_date - self.due_date).days
            penalty = days_delayed * 2.00
            return -penalty
        else:
            return 0.00


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13)
    publisher = models.CharField(max_length=255)
    pub_year = models.IntegerField()
    image_url = models.URLField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.title
