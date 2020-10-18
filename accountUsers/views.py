import validate_email
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMessage, send_mail, EmailMultiAlternatives
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.views import View
from django.urls import reverse
# for creating and sending link and code to user for activation
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from .codeGenerator import token_generator

from accountUsers.forms import RegistrationForm, UserAuthenticationForm, AccountUpdateForm

# Create your views here.
from accountUsers.models import accountUsers
from household import settings
import threading


# to send email faster
class EmailThread(threading.Thread):
    def __init__(self, send_email):
        self.send_email = send_email
        threading.Thread.__init__(self)

    def run(self):
        self.send_email.send(fail_silently=False)


def registration_view(request):
    context = {}
    print('register here')
    user = request.user
    if user.is_authenticated:
        return redirect('calculation:dashboard')
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            print('form valid')
            email = form.cleaned_data.get('email')
            is_valid = validate_email.validate_email(email, verify=True)  # validating email for existing one
            if is_valid:
                form.save()
                form.save()
                toemail = form.cleaned_data.get('email')
                send_activation_email(request, toemail)

                raw_password = form.cleaned_data.get('password1')
                # account = authenticate(email=email, password=raw_password)
                # login(request, account)
                print('send redirect')
                context = {
                    'successMessage': 'Account created successfully. Please check your email to activate.',
                    'class': 'text-success',
                }
                return render(request, 'accountUsers/register.html', context)
            else:
                context = {
                    'successMessage': 'Please enter valid email address to register.',
                    'registration_form': form,
                    'class': 'text-danger',
                }
                return render(request, 'accountUsers/register.html', context)
        else:  # GET request
            print('else valid')
            context = {
                'registration_form': form,
                'failMessage': 'Account not created.',
                'class': 'text-danger',
            }
            return render(request, 'accountUsers/register.html', context)
    else:
        print('form')
        form = RegistrationForm()
        context = {
            'registration_form': form, }
    return render(request, 'accountUsers/register.html', context)


def resend_activation_link(request):
    context = {}
    print(request.POST)
    if request.POST:
        email = request.POST['email']
        try:
            user = accountUsers.objects.get(email=email)
            if user.is_active:
                context = {
                    'message': 'This user is already active.'
                }
            else:
                send_activation_email(request, email)
                context = {
                    'message': 'Activation Link sent. Please check your email and activate.'
                }
        except accountUsers.DoesNotExist:

            context = {
                'message': 'This account is not in the system. Please register.',

            }

    return render(request, 'registration/resendActivationLink.html', context)


def send_activation_email(request, toemail):
    email_subject = 'Activate your account'
    user = accountUsers.objects.get(email=toemail)
    # path_to_view
    # - getting domain we are on
    # - relative url to verification
    # - encode uid
    # - token

    uidb64 = urlsafe_base64_encode(force_bytes(user))
    domain = get_current_site(request).domain
    link = reverse('activate', kwargs={'uidb64': uidb64, 'token': token_generator.make_token(user)})
    activate_url = 'http://' + domain + link

    email_body = 'Hi ' + toemail + ', ' + 'Use the below link to activate you account \n' + activate_url
    from_email = settings.EMAIL_HOST_USER
    to_email = [toemail]
    send_email = EmailMultiAlternatives(
        email_subject,
        email_body,
        from_email,
        to_email,
    )
    EmailThread(send_email).start()


class VerificationView(View):
    def get(self, request, uidb64, token):
        context = {}
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = accountUsers.objects.get(email=uid)
            print(user.is_active, 'is active', user)

        except Exception as identifier:
            user = None
            context = {
                'activationMessage': 'Something went wrong. Please re request the activation link below.',
                'success': 'fail',
            }

        if user is not None and token_generator.check_token(user, token):
            print(user.is_active)
            if user.is_active:
                print('sssssssssssssssssssss')
                context = {
                    'activationMessage': 'Account already activated. Login to get access.',
                    'success': 'already',
                }

            user.is_active = True
            user.save()
            print('ttttttttttttttttttttttt')
            context = {
                'activationMessage': 'Account activation successful.',
                'success': 'success',
            }

        else:
            context = {
                'activationMessage': 'The activation link is expired or broken. ',
                'success': 'fail',
            }
        return render(request, 'registration/activationMessage.html', context)


class registerFromInvite(View):
    def post(self, request, uidb64):
        print(request.POST)
        ret = registration_view(request)

        print('return value', ret)
        return ret

    def get(self, request, uidb64):
        form = RegistrationForm
        context = {}
        uid = force_text(urlsafe_base64_decode(uidb64))
        try:
            print('1')
            user = accountUsers.objects.get(email=uid)
            if user:
                print('2')
                context = {
                    'email': uid,
                    'alreadyRegistered': 'This email is already registered.',
                }
                return render(request, 'accountUsers/alreadyRegistered.html', context)

        except accountUsers.DoesNotExist:
            print('3')
            user = None
            context = {
                'email': uid,
                'registration_form': form,
            }
        return render(request, 'accountUsers/register.html', context)


def inviteEmail(request):
    template = 'groups/addedMessage.html'
    context = {}
    print(request.user, request.POST)
    if request.POST:
        inviteEmail = request.POST['inviteEmail']

        is_valid = validate_email.validate_email(inviteEmail, verify=True)
        if is_valid:
            email_subject = 'Invitaion to register'
            uidb64 = urlsafe_base64_encode(force_bytes(inviteEmail))
            domain = get_current_site(request).domain
            # link = reverse('registerFromInvite', kwargs={'uidb64': uidb64, 'token': token_generator.make_token(inviteEmail)})
            activate_url = 'http://' + domain + '/register/' + uidb64
            email_body = 'Hi,\n ' + str(
                request.user) + ' has invited you to join his group. ' + 'Use the below link to register new account \n' + activate_url
            from_email = settings.EMAIL_HOST_USER
            to_email = [inviteEmail]
            send_email = EmailMultiAlternatives(
                email_subject,
                email_body,
                from_email,
                to_email,

            )
            EmailThread(send_email).start()
            if send_email:
                context = {
                    'inviteEmailMessage': 'Invitation sent.',
                    'class': 'text-success'
                }
            else:
                context = {
                    'inviteEmailMessage': 'Invitation could not be sent.',
                    'class': 'text-danger'
                }
        else:
            context = {
                'inviteEmailMessage': 'This email does not exists.',
                'class': 'text-danger'
            }
    if request.is_ajax():
        html = render_to_string(template, context, request=request)
    return JsonResponse({'post': html})


def logout_view(request):
    logout(request)
    return redirect('calculation:index')


def login_view(request):
    context = {}
    user = request.user
    print(request.POST)
    if user.is_authenticated:
        return redirect('calculation:my_profile')
    if request.POST:
        form = UserAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)

            if user:
                login(request, user)
                context['user'] = user

                return redirect('calculation:my_profile')

    else:
        form = UserAuthenticationForm()
    context['login_form'] = form
    return render(request, 'accountUsers/login.html', context)


def account_view(request):
    if not request.user.is_authenticated:
        return redirect('index')
    context = {}

    if request.POST:
        print(request.POST)
        print(request.FILES)
        try:
            myfile = request.FILES['pro_pic']
        except:
            myfile = ''
        print(myfile)
        form = AccountUpdateForm(request.POST, request.FILES or None, instance=request.user)
        if form.is_valid():
            print('validddid')
            form.initial = {
                "username": request.POST['username'],
                "first_name": request.POST['first_name'],
                "user_dob": request.POST['user_dob'],
                "user_address": request.POST['user_address'],
                "pro_pic": myfile,

            }
            # fs = FileSystemStorage()
            # fs.save(myfile.name, myfile)
            account = accountUsers.objects.get(username=request.POST['username'])
            account.pro_pic = myfile

            account.save()
            form.save()
            context['success_message'] = 'Updated'
    else:
        pro_pic = request.user.pro_pic
        print(pro_pic)
        form = AccountUpdateForm(
            initial={
                "last_name": request.user.last_name,
                "username": request.user.username,
                "first_name": request.user.first_name,
                "user_dob": request.user.user_dob,
                "user_address": request.user.user_address,
                "pro_pic": pro_pic,
            }
        )
    context['account_form'] = form
    return render(request, 'accountUsers/account.html', context)


def prameshshrestha(request):
    template = 'pramesh/index.html'
    template1 = 'pramesh/emailSent.html'
    context = {}
    if request.POST:
        print(request.POST)
        name = request.POST['name']
        f_email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']
        to_email = 'masterpramesh@gmail.com'

        email_body = 'Message from \n' + 'Name = ' + name + '\n' + 'Email = ' + f_email + '\n' + message
        from_email = f_email
        to_email = [to_email]
        send_email = EmailMultiAlternatives(
            subject,
            email_body,
            from_email,
            to_email,
        )

        EmailThread(send_email).start()
        context = {
            'message': 'email sent'
        }
        print(send_email)
        if send_email:
            print('positive')
            return render(request, template1, context)
    else:
        return render(request, template, context)
