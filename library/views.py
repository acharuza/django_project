import os

from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .forms import SearchForm
from .models import Book, Reservation, CheckedOutBook
from .models import Reader, ReaderManager
from .forms import UserRegisterForm
from .forms import ReservationForm
from django.contrib.auth import login, authenticate
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from django.contrib import messages
from .forms import FilterReservationsForm
from django.utils import timezone
from lxml import etree


def index(request):
    """
    View function for rendering the main index page.

    This view function handles the rendering of the main index page, typically representing the home page of the
    website. It initializes a SearchForm using the request's GET parameters, if any, and passes it to the
    'index.html' template.

    :param request: (HttpRequest) The HTTP request object.
    :return: The rendered HTML response containing the 'index.html' template with the initialized SearchForm.
    """
    form = SearchForm(request.GET or None)
    return render(request, 'index.html', {'form': form})


def search_results(request):
    """
    View function for handling search results.

    This view function processes the search form submitted via GET request. It initializes a SearchForm using the
    request's GET parameters and validates it. If the form is valid, it extracts the search query from the cleaned
    data and filters books by Title, Author and ISBN. The results are then passed to the 'search_results.html'
    template for rendering.

    :param request: (HttpRequest) The HTTP request object.
    :return: The rendered HTML response containing the 'search_results.html' template with search results.
    """
    form = SearchForm(request.GET)

    if form.is_valid():
        query = form.cleaned_data.get('q', '')
        books = Book.objects.all()

        if query:
            books = books.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(isbn__icontains=query)
            )
        else:
            books = []
    else:
        query = ''
        books = []

    return render(request, 'search_results.html', {'query': query,
                                                   'books': books,
                                                   'form': form})


def book_view(request, book_id):
    """
    View function for displaying details of a specific book and handling reservations.

    This view function retrieves the details of a book with the given ID from the database.
    If the request method is POST, it initializes a ReservationForm using the POST data.
    Otherwise, it initializes an empty ReservationForm.
    The book details and the reservation form are then passed to the 'book.html' template for rendering.

    :param request: (HttpRequest) The HTTP request object.
    :param book_id: (int) The ID of the book to display.
    :return: The rendered HTML response containing the 'book.html' template with book details and reservation form.
    """
    book = Book.objects.get(id=book_id)
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            book.is_available = False
            reservation.book = book
            reservation.reader = request.user
            reservation.save()
    else:
        form = ReservationForm()
    return render(request, 'book.html', {'book': book,
                                         'form': form})


def sign_up(request):
    """
    View function for handling user registration.

    This view function handles both GET and POST requests for user registration.
    If the request method is POST, it initializes a UserRegisterForm using the POST data.
    If the form is valid, it creates a new user, sets the password, and logs the user in.
    The user is then redirected to the 'verify_email' page.
    If the request method is GET, it initializes an empty UserRegisterForm.
    The form is then passed to the 'registration/signup.html' template for rendering.

    :param request: (HttpRequest) The HTTP request object.
    :return: The rendered HTML response containing the 'registration/signup.html' template with the registration form.
    """
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password1')
            user.set_password(password)
            user.save()
            new_user = authenticate(email=user.email, password=password)
            login(request, new_user)
            return redirect('verify_email')

    else:
        form = UserRegisterForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required(login_url='/library/login')
def account(request):
    request.user.update_balance()
    form = FilterReservationsForm(request.GET)
    reservations = Reservation.objects.all()
    checked_out_books = CheckedOutBook.objects.all()
    reservations = reservations.filter(reader=request.user)
    checked_out_books = checked_out_books.filter(reader=request.user, end_date__lte=timezone.now().date())

    if form.is_valid():
        from_date = form.cleaned_data.get('from_date')
        to_date = form.cleaned_data.get('to_date')
        only_active = form.cleaned_data.get('only_active')

        if from_date and to_date:
            reservations = reservations.filter(
                start_date__lte=to_date,
                end_date__gte=from_date,
            )
        if only_active:
            reservations = reservations.filter(
                is_active=True,
            )

    xml_content_res = generate_xml(reservations, True)
    xml_content_check = generate_xml(checked_out_books, False)
    with open("library\\static\\reservations.xslt", encoding='utf-8') as file:
        xslt_content_res = file.read()
    with open("library\\static\\checked_out_books.xslt", encoding='utf-8') as file:
        xslt_content_check = file.read()
    result_html_res = transform_xml(xml_content_res, xslt_content_res)
    result_html_check = transform_xml(xml_content_check, xslt_content_check)

    return render(request, 'account.html', {'result_html_res' : result_html_res,
                                            'form' : form,
                                            'result_html_check' : result_html_check})


def generate_xml(data, is_reservation):
    if is_reservation:
        xml_content = "<reservations>\n"
        for reservation in data:
            xml_content += f"\t<reservation>\n\t\t<book>{reservation.book}</book>\n\t\t"
            xml_content += f"<start_date>{reservation.start_date}</start_date>\n\t\t"
            xml_content += f"<end_date>{reservation.end_date}</end_date>\n\t\t"
            xml_content += f"<is_active>{reservation.is_active}</is_active>\n\t\t"
            xml_content += f"<should_remind>{reservation.should_remind}</should_remind>\n\t\t"
            xml_content += f"<add_info>{reservation.add_info}</add_info>\n\t</reservation>\n"
        xml_content += "</reservations>"
    else:
        xml_content = "<checked_out_books>\n"
        for checked_out_book in data:
            xml_content += f"\t<checked_out_book>\n\t\t<book>{checked_out_book.book}</book>\n\t\t"
            xml_content += f"<start_date>{checked_out_book.start_date}</start_date>\n\t\t"
            xml_content += f"<due_date>{checked_out_book.due_date}</due_date>\n\t\t"
            xml_content += f"<end_date>{checked_out_book.end_date}</end_date>\n\t\t"
            xml_content += f"<penalty>{checked_out_book.calculate_penalty()}</penalty>\n\t</checked_out_book>\n"
        xml_content += "</checked_out_books>"
    return xml_content


def transform_xml(xml_string, xslt_string):
    xml_tree = etree.fromstring(xml_string.encode('utf-8'))
    xslt_tree = etree.fromstring(xslt_string.encode('utf-8'))
    transform = etree.XSLT(xslt_tree)
    result_tree = transform(xml_tree)
    result_html = etree.tostring(result_tree, pretty_print=True, encoding='utf-8').decode('utf-8')
    return result_html


def verify_email(request):
    """
    View function for handling email verification.

    This view function handles both GET and POST requests for email verification.
    If the request method is POST and the user's email is not verified, it sends a verification email.
    The verification email includes a link with a unique token to confirm the user's email.
    If the user's email is already verified, they are redirected to the 'sign_up' page.
    If the request method is GET, it renders the 'verify_email/verify_email.html' template.

    :param request: (HttpRequest) The HTTP request object. :return: Redirects to 'verify_email_done' if a
    verification email is sent successfully. Redirects to 'sign_up' if the user's email is  already verified. Renders
    'verify_email/verify_email.html' template for GET requests.
    """
    if request.method == "POST":
        if not request.user.email_is_verified:
            current_site = get_current_site(request)
            user = request.user
            email = request.user.email
            subject = "Verify Email"
            message = render_to_string('verify_email/verify_email_message.html', {
                'request': request,
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            email = EmailMessage(
                subject, message, to=[email]
            )
            email.content_subtype = 'html'
            email.send()
            return redirect('verify_email_done')
        else:
            return redirect('sign_up')
    return render(request, 'verify_email/verify_email.html')


def verify_email_done(request):
    return render(request, 'verify_email/verify_email_done.html')


def verify_email_confirm(request, uidb64, token):
    """
    View function for handling email verification confirmation.

    This view function processes the confirmation link sent in the email.
    It decodes the UID and checks the validity of the token.
    If the link is valid, it updates the user's email verification status and displays a success message.
    If the link is invalid, it displays a warning message.

    :param request: (HttpRequest) The HTTP request object.
    :param uidb64: (str) The base64-encoded UID of the user.
    :param token: (str) The token used for email verification.
    :return: Redirects to 'verify_email_complete' on successful verification. Renders
    'verify_email/verify_email_confirm.html' template on invalid link.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Reader.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Reader.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.email_is_verified = True
        user.save()
        messages.success(request, 'Your email has been verified.')
        return redirect('verify_email_complete')
    else:
        messages.warning(request, 'The link is invalid.')
    return render(request, 'verify_email/verify_email_confirm.html')


def verify_email_complete(request):
    return render(request, 'verify_email/verify_email_complete.html')
