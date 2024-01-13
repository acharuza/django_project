from django.contrib import admin
from django.contrib.admin.templatetags import admin_urls

from .models import Book
from .models import Reservation
from .models import Reader
from .models import CheckedOutBook


class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn',
                    'publisher', 'pub_year',
                    'image_url', 'is_available']
    search_fields = ['title', 'author', 'isbn',
                     'publisher', 'pub_year', 'is-available']


class ReaderAdmin(admin.ModelAdmin):
    list_display = ['email', 'email_is_verified',
                    'first_name', 'last_name',
                    'balance', 'is_superuser']
    search_fields = ['email', 'email_is_verified',
                     'first_name', 'last_name',
                     'balance', 'is_superuser']


@admin.action(description="Mark selected reservations as inactive if their end date passed")
def end_reservations(self, request, queryset):
    for reservation in queryset:
        reservation.end_reservation()


class ReservationAdmin(admin.ModelAdmin):
    list_display = ['reader', 'book', 'start_date',
                    'end_date', 'is_active',
                    'should_remind', 'add_info']
    search_fields = ['reader', 'book', 'start_date',
                     'end_date', 'is_active',
                     'should_remind']
    actions = [end_reservations]

    def delete_model(self, request, obj):
        obj.book.is_available = True
        obj.delete()


class CheckedOutBookAdmin(admin.ModelAdmin):
    list_display = ['book', 'reader', 'start_date',
                    'due_date', 'end_date']
    search_fields = ['book', 'reader', 'start_date',
                     'due_date', 'end_date']


admin.site.register(Book, BookAdmin)
admin.site.register(Reader, ReaderAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(CheckedOutBook, CheckedOutBookAdmin)
