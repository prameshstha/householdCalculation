"""household URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from accountUsers.views import (
    registration_view,
    logout_view, login_view,
    account_view, VerificationView, resend_activation_link, inviteEmail, registerFromInvite, prameshshrestha)
from django.conf import settings

app_name = 'household'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('calculation.urls'), name='calculation'),
    path('register/', registration_view, name='register'),
    path('register/<uidb64>', registerFromInvite.as_view(), name='register1'),
    path('inviteEmail/', inviteEmail, name='inviteEmail'),
    path('resend_activation_link/', resend_activation_link, name='resend_activation_link'),
    path('activate/<uidb64>/<token>/', VerificationView.as_view(), name='activate'),
    # path('registerFromInvite/<uidb64>/<token>/', registerFromInvite.as_view(), name='registerFromInvite'),
    path('logout/', logout_view, name='logout'),
    path('login/', login_view, name='login'),
    path('account/', account_view, name='account'),
    path('prameshshrestha/', prameshshrestha, name='prameshshrestha'),

    # Password reset links (ref: https://github.com/django/django/blob/master/django/contrib/auth/views.py)
    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_complete.html'),
         name='password_change_done'),

    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html'),
         name='password_change'),

    # Email sent success message
    path('password_reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_done1.html'),
         name='password_reset_done'),

    # Link to password reset form in email
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm1.html'), name='password_reset_confirm'),

    # Submit email form
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form1.html'), name='password_reset'),

    # Password successfully changed message
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_completed.html'),
         name='password_reset_complete'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)