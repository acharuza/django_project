from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Reader, Reservation
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class SearchForm(forms.Form):
    """
    Form responsible for book searching in library app based on Django's forms.Form.

    Attributes:
        - q (CharField): Text field used for input of a search query.

    Example Usage:
    form = SearchForm(request.GET)
    if form.is_valid():
        # Proccess and handle search results.
    else:
        # Handle the case when the form is invalid.
    """
    q = forms.CharField(label="",
                        widget=forms.TextInput(attrs={'class': 'search_text',
                                                      'placeholder': 'Search by Title, Author or ISBN'}),
                        required=False)


class UserRegisterForm(UserCreationForm):
    """
    Custom user registration form for library.Reader user based on Django's UserCreationForm

    Attributes:
        - first_name (CharField): Field for entering the user's first name.
        - last_name (CharField): Field for entering the user's last name.
        - email (EmailField): Field for entering the user's email address.
        - password1 (CharField): First password entry field.
        - password2 (CharField): Second password entry field for password confirmation.

    Methods:
        - clean(): Custom clean method to perform additional validation on form data.
        Checks for existing email addresses and ensures a minimum password length.

    Meta:
        - model (Reader): Specifies the User model associated with this form.
        - fields: List of fields to be included in the form.

    Example usage:
    form = UserRegisterForm(request.POST)
    if form.is_valid():
        # Process and handle user registration.
    else:
        # Handle the case when the form is invalid, e.g., display error messages.

    Note:
        - This form is designed for registering users in the system and is associated with the Reader user.
    """

    class Meta:
        model = Reader
        fields = [
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        ]

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password1')
        email_check = Reader.objects.filter(email=email)
        if email_check.exists():
            raise forms.ValidationError('This Email already exists')
        if len(password) < 5:
            raise forms.ValidationError('Your password should have more than 5 characters')
        return super(UserRegisterForm, self).clean(*args, **kwargs)


class ReservationForm(forms.Form):
    """
    Form for making a reservation based on Django's forms.Form.

    This form allows users to reserve a resource, specifying the start date, reservation duration,
    preference for a reminder, and providing additional information.

    Attributes:
        - start_date (DateField): Field for entering the reservation start date.
        - how_long (IntegerField): Field for specifying the reservation duration in days.
        - should_remind (BooleanField): Checkbox indicating whether the user wishes to receive a reservation reminder via email.
        - add_info (CharField): Field for entering additional information for the staff (optional).

    Example Usage:
    form = ReservationForm(request.POST)
    if form.is_valid():
        # Process and handle the reservation.
    else:
        # Handle the case when the form is invalid, e.g., display error messages.

    Note:
        - The start_date field is initialized with the current date and includes a validator to ensure it's not in the past.
        - The how_long field has validators to enforce a minimum of 1 day and a maximum of 5 days.
        - Users can optionally choose to receive a reservation reminder via email.
        - The add_info field allows users to provide additional helpful information for the staff.
    """
    start_date = forms.DateField(label='Start date:', widget=forms.DateInput(attrs={'type': 'date',
                                                                                    'value' : timezone.now().date()}),
                                 validators=[MinValueValidator(timezone.now().date())])
    how_long = forms.IntegerField(label='Reservation duration in days:',
                                  help_text='Maximum allowed duration is 5 days.',
                                  initial=3,
                                  validators=[MinValueValidator(1), MaxValueValidator(5)])
    should_remind = forms.BooleanField(label='Do you wish to receive a reservation reminder via email?', initial=True,
                                       required=False)
    add_info = forms.CharField(label='Additional information for our staff:',
                               widget=forms.Textarea(attrs={
                                   'placeholder': 'Here you can share additional info that might be helpful for our ' +
                                                  'staff e.g.' +
                                                  'time of the day we can expect you. This is not required but it ' +
                                                  'will be greatly appreciated!'}),
                               required=False)

    class Meta:
        model = Reservation
        fields = ['start_date',
                  'how_long',
                  'should_remind',
                  'add_info']

    def save(self, commit=True):
        start_date = self.cleaned_data['start_date']
        how_long = self.cleaned_data['how_long']
        should_remind = self.cleaned_data['should_remind']
        add_info = self.cleaned_data['add_info']

        end_date = start_date + timezone.timedelta(days=how_long)
        if start_date <= timezone.now().date() <= end_date:
            is_active = True
        else:
            is_active = False

        reservation = Reservation(
            start_date=start_date,
            end_date=end_date,
            should_remind=should_remind,
            add_info=add_info,
            is_active=is_active
        )

        if commit:
            reservation.save()

        return reservation

class FilterReservationsForm(forms.Form):
    from_date = forms.DateField(label='From:', widget=forms.DateInput(attrs={'type' : 'date',
                                                                             'value' : timezone.now().date()}))
    to_date = forms.DateField(label='To:', widget=forms.DateInput(attrs={'type' : 'date',
                                                                         'value' : timezone.now().date() + timezone.timedelta(days=7)}))
    only_active = forms.BooleanField(label='Only active reservations?', initial=True, required=False)
