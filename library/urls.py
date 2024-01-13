from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_results, name='search_results'),
    path('books/<int:book_id>', views.book_view, name='book'),
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('signup/', views.sign_up, name="sign_up"),
    path('account/', views.account, name="account"),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('verify-email/done/', views.verify_email_done, name='verify_email_done'),
    path('verify-email/confirm/<uidb64>/<token>/', views.verify_email_confirm, name='verify_email_confirm'),
    path('verify-email/complete/', views.verify_email_complete, name='verify_email_complete'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete')
]
