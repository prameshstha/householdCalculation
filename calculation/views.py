from decimal import Decimal
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core import serializers
from django.core.exceptions import ValidationError
from django.core.mail import send_mail, EmailMultiAlternatives
from django.http import request, JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.template.loader import render_to_string
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.html import strip_tags

from accountUsers.forms import RegistrationForm
from accountUsers.views import EmailThread, registration_view
from calculation.form import ExpensesForm
from calculation.models import Groups, Expenses, final_calculation, PersonalTotal, FinalTransaction, CalculationPeriod, \
    GroupType
from accountUsers.models import accountUsers
from household import settings


def index(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        return redirect('calculation:dashboard')
    if request.POST:
        ret = registration_view(request)
        return ret
    else:
        form = RegistrationForm()
        context['registration_form'] = form
    return render(request, 'household/index.html', context)


def test(request):
    context = {
        'a': 'a',
    }
    return render(request, 'calculation/test.html', context)


def my_profile(request):
    context = {}
    template = 'accountUsers/my_profile.html'
    return render(request, template, context)


@login_required
def create_group(request):
    groupType = GroupType.objects.all()
    template = 'groups/create_group.html'
    context = {'groupType': groupType}
    if request.POST:
        group_pic = request.FILES.get('groupPic')
        print(group_pic)
        print(request.POST, request.user)
        print(request.FILES)
        group_type = request.POST['GroupType']
        group_name = request.POST['GroupName']
        country_name = request.POST['Country']
        member_count = request.POST['MemberCount']

        ob = Groups.objects.filter(group_name=group_name, group_admin=request.user)
        if ob:
            context = {
                'message': 'You have already created a group with this name ' + '"' + group_name + '"',
            }
            return render(request, 'groups/create_group.html', context)
        else:
            created = Groups.objects.create(
                group_name=group_name,
                group_type=group_type,
                group_country=country_name,
                group_admin=request.user,
                group_pic=group_pic,
            )
            if created:
                created.group_members.add(request.user)
                print(created)
                context = {
                    'messageSuccess': 'New group created.' + '"' + group_name + '" Go to dashboard to view activities. ',
                }
    return render(request, template, context)


@login_required()
def edit_group(request, g_id=None):
    template = 'groups/edit_group.html'
    if request.POST:
        print(request.POST)
        print(request.FILES)
        group_type = request.POST['GroupType']
        country_name = request.POST['Country']
        try:
            group_pic = request.FILES['groupPic']
        except:
            group_pic = ''
        member_count = request.POST['MemberCount']
        group_instance = Groups.objects.get(id=g_id)
        group_instance.group_type = group_type
        group_instance.country_name = country_name
        group_instance.group_pic = group_pic
        try:
            print('a', group_instance.id)
            print(group_instance.save())
            group_instance.save()

            context = {
                'messageSuccess': 'Group details updated. Go to dashboard to view activities. ',
            }
        except Exception as e:
            print(e, 'errorrr')
            context = {
                'message': 'Update fail. Try again',
            }
        return render(request, template, context)

    else:
        print('not post', g_id)
        groupType = GroupType.objects.all()

        group = Groups.objects.get(id=g_id)
        print(group.group_admin, request.user)
        if group.group_admin == request.user:
            context = {
                'group': group,
                'groupType': groupType,
            }
            return render(request, template, context)
        else:
            return redirect('http://localhost:8000/')


@login_required
def dashboard(request):
    selected_groups = Groups.objects.filter(group_members=request.user)
    created_groups = Groups.objects.filter(group_admin=request.user)
    cal_period = CalculationPeriod.objects.filter(group_id__in=selected_groups, is_active=True)
    created_cal_period = CalculationPeriod.objects.filter(group_id__in=created_groups, is_active=True)
    # calculate total balance
    final_trans = FinalTransaction.objects.filter(calculation_period__in=cal_period)
    print(final_trans)
    print('trasnnndlkfj')
    owe = 0
    owned = 0
    for u in final_trans:
        print(u)
        print(u.to_user)
        if u.to_user == request.user:
            owned += u.amount
        if u.from_user == request.user:
            owe += u.amount

    print('ffffffffffffffffff', owe, owned)
    total_balance = owned - owe

    # print(cal_period, selected_groups)
    # for f in cal_period:
    #     print(f.group_id)
    print('noo')
    group_json = serializers.serialize("json", created_groups)
    created_cal_period_json = serializers.serialize("json", created_cal_period)
    selected_groups_json = serializers.serialize("json", selected_groups)
    all_activities = Expenses.objects.filter(calculation_period__in=cal_period).order_by('-id')
    print(all_activities)
    # final_calculation(1)

    # # print(all_activities.query)
    # for a in all_activities:
    #     print(a.group_id, a.amount, a.spender, a.spender.username)
    # print(selected_groups, created_groups,'json strats', group_json)
    ExpForm = ExpensesForm
    context = {
        'all_groups': selected_groups,
        'created_groups': created_groups,
        'group_json': group_json,
        'selected_groups_json': selected_groups_json,
        'ExpensesForm': ExpForm,
        'all_activities': all_activities,
        'owe': owe,
        'owned': owned,
        'total_balance': total_balance,
        'created_cal_period_json': created_cal_period_json,
    }
    template = 'groups/dashboard.html'
    return render(request, template, context)


@login_required
def addMember(request):
    print(request.POST)
    template = 'groups/addedMessage.html'
    template1 = 'groups/showGroupMemberNewCycle.html'
    NewEmail = request.POST['newMember']
    group_id = request.POST['groupName']
    group = Groups.objects.get(id=group_id)
    try:
        member = accountUsers.objects.get(email=NewEmail)
        try:
            memberInGroup = Groups.objects.get(group_members=member, id=group_id)
            context = {
                'memberAdded': 'This member already exists this group.'
            }
        except Groups.DoesNotExist:

            addInGroup = group.group_members.add(member)
            try:
                memberInGroup = Groups.objects.get(group_members=member, id=group_id)
                domain = get_current_site(request).domain
                dashboard_link = 'http://' + domain + '/dashboard/'
                context = {
                    'memberAdded': 'New member added in the group ' + group.group_name + '.',
                    'memberIngroup': memberInGroup,
                    'group': memberInGroup,
                    'user': request.user.first_name + ' ' + request.user.last_name,
                    'dashboard_link': dashboard_link,
                    'userEmail': request.user.email,
                }

                #     send email to new member
                email_subject = request.user.username + ' added you to group ' + "'" + str(group) + "'"
                html_message = render_to_string('email/addMember.html', context)
                plain_message = strip_tags(html_message)
                from_email = settings.EMAIL_HOST_USER
                to_email = [NewEmail]

                email_body = plain_message

                send_email = EmailMultiAlternatives(
                    email_subject,
                    email_body,
                    from_email,
                    to_email,

                )
                send_email.attach_alternative(html_message, "text/html")
                EmailThread(send_email).start()


            except Groups.DoesNotExist:
                context = {
                    'memberAdded': 'Member not added in ' + group_id + '.'
                }
    except accountUsers.DoesNotExist:
        context = {
            'memberIngroup': group,
            'memberAdded': 'This email address does not have account in this app. Do you want to invite them? '
        }
    except accountUsers.MultipleObjectsReturned:
        context = {
            'memberAdded': 'Something is wrong. Please try again. '
        }
    if request.is_ajax():
        html = render_to_string(template, context, request=request)
        groupMemberCycle = render_to_string(template1, context, request=request)
        newMember = render_to_string('groups/showGroupMember.html', context, request=request)
    return JsonResponse({'post': html, 'groupMemberCycle': groupMemberCycle, 'newMember': newMember})


def deleteMember(request):
    if request.POST:
        print(request.POST)
        template1 = 'groups/showGroupMemberNewCycle.html'
        member_id = request.POST['member_id']
        group_id = request.POST['group_id']
        group = Groups.objects.get(id=group_id)
        try:
            cal_period = CalculationPeriod.objects.get(group_id=group_id, is_active=True)
            print(cal_period)
            context = {
                'memberIngroup': group,
                'messageNoDelete': 'Deletion failed. Calculation period is still active. Settle calculation first and '
                                   'try again. '
            }
        except CalculationPeriod.DoesNotExist:
            group.group_members.remove(member_id)
            context = {
                'memberIngroup': group,
                'messageDelete': 'Member deleted.'
            }

    if request.is_ajax():
        html = render_to_string('groups/showGroupMember.html', context, request=request)
        groupMemberCycle = render_to_string(template1, context, request=request)
    return JsonResponse({'post': html, 'groupMemberCycle': groupMemberCycle})


def makeAdmin(request):
    print('make admin')
    if request.POST:
        print(request.POST)
        group_id = request.POST['g_id']
        member_id = request.POST['m_id']
        member = accountUsers.objects.get(id=member_id)
        group_instance = Groups.objects.get(id=group_id)
        print(member, group_instance, '-==-=================')
        group_instance.group_admin = member

        #     send email to new member
        domain = get_current_site(request).domain
        dashboard_link = 'http://' + domain + '/dashboard/'
        email_subject = request.user.first_name + ' has added you as group admin of ' + "'" + str(group_instance) + "'"
        email_body = request.user.first_name + ' has added you as group admin of ' + "'" + str(group_instance) + "'.\n" + 'Visit link below to access website\n' + dashboard_link
        from_email = settings.EMAIL_HOST_USER
        to_email = [member.email]

        send_email = EmailMultiAlternatives(
            email_subject,
            email_body,
            from_email,
            to_email,

        )
        EmailThread(send_email).start()



        try:
            group_instance.esave()
        except Exception as e:
         print(e, 'errorrr')

    return redirect('calculation:dashboard')


def searchMembers(request):
    print(request.POST)
    searchType = request.POST['search']
    if request.method == 'POST':
        searchTxt = request.POST['searchText']
        print(searchTxt)
        searchUser = accountUsers.objects.filter(email__icontains=searchTxt)
        print(searchUser)
    else:
        searchTxt = ''
        searchUser = None
    context = {'searchUser': searchUser}
    if searchType == 'addMembers':
        if request.is_ajax():
            html = render_to_string('groups/ajax_search.html', context, request=request)
        return JsonResponse({'search': html})
    elif searchType == 'searchFriends':
        if request.is_ajax():
            html = render_to_string('groups/searchFriends.html', context, request=request)
        return JsonResponse({'search': html})


def addFriendMember(request):
    print('addedFriendMessage')
    print(request.POST)
    group_name = request.POST['groupName']
    friend_id = request.POST['friendId']
    try:
        get_group = Groups.objects.get(group_name=group_name, group_members=friend_id)
        context = {
            'memberAdded': 'This user is already in this group.'
        }
    except Groups.DoesNotExist:
        group = Groups.objects.get(group_name=group_name)
        group.group_members.add(friend_id)

        context = {
            'memberAdded': 'New member added in the group.'
        }
    if request.is_ajax():
        html = render_to_string('groups/addedMessage.html', context, request=request)
    return JsonResponse({'post': html})


def getMemberOfGroup(request):
    group_id = request.POST['groupName']
    print('get members', request.POST)
    # seleected_group = Groups.objects.get(id=group_id)

    template1 = 'groups/GroupRecentActivities.html'
    template2 = 'groups/Final_Transactions.html'
    template3 = 'groups/showGroupMemberNewCycle.html'
    memberIngroup = Groups.objects.get(id=group_id)
    try:
        cal_period = CalculationPeriod.objects.get(group_id=group_id, is_active=True)
        # need to edit
        # created_cal_period_json = serializers.serialize("json", cal_period)
        print('cal period', cal_period)
        g_expenses = Expenses.objects.filter(group_id=group_id, calculation_period=cal_period).order_by('-added')
        if g_expenses:
            group_expenses = g_expenses
        else:
            group_expenses = ''
        final_transaction = FinalTransaction.objects.filter(group_id=group_id, calculation_period=cal_period).order_by(
            '-id')

        print(group_id, final_transaction)
        # toUser = FinalTransaction.objects.filter(group_id=group_id, calculation_period=calculation_period).aggregate(
        #     totalExpenses=Sum('total_amount'))
        print('final transation')
        owe = 0
        owned = 0
        for u in final_transaction:
            print(u.to_user)
            if u.to_user == request.user:
                owned += u.amount
            if u.from_user == request.user:
                owe += u.amount

        print('ffffffffffffffffff', owe, owned)
        total_balance = owned - owe
        context = {
            'memberAdded': 'New member added in the group ' + 'group_name' + '.',
            'memberIngroup': memberIngroup,
            'group_expenses': group_expenses,
            'final_transaction': final_transaction,
            'owe': owe,
            'owned': owned,
            'total_balance': total_balance,
            'cal_period': cal_period,
            'ActiveCalculationPeriod': 'Calculation period is active from: ' + str(cal_period.start_period) + '.'
        }
        if request.is_ajax():
            html = render_to_string('groups/showGroupMember.html', context, request=request)
            group_activities = render_to_string(template1, context, request=request)
            final_transaction = render_to_string(template2, context, request=request)
        return JsonResponse({'post': html, 'group': group_activities, 'final_transaction': final_transaction})
    except CalculationPeriod.DoesNotExist:
        context = {
            'ActiveCalculationPeriod': 'No active calculation period for this group.',
            'memberIngroup': memberIngroup,
            'owe': 0,
            'owned': 0,
            'total_balance': 0,
            'final_transaction': ''
        }
        print(context)
        if request.is_ajax():
            html = render_to_string('groups/showGroupMember.html', context, request=request)
            group_activities = render_to_string(template1, context, request=request)
            groupMemberCycle = render_to_string(template3, context, request=request)
            final_transaction = render_to_string(template2, context, request=request)
        return JsonResponse({'post': html, 'group': group_activities, 'groupMemberCycle': groupMemberCycle,
                             'final_transaction': final_transaction})


def addExpenses(request):
    template = 'groups/addedMessage.html'
    template1 = 'groups/GroupRecentActivities.html'
    template2 = 'groups/Final_Transactions.html'
    template4 = 'groups/expensesAdded.html'
    print(request.FILES)
    print(request.POST)
    group_id = request.POST['group_id']
    amt = request.POST['amount']
    try:
        bill = request.FILES['bill']
    except MultiValueDictKeyError:
        context = {
            'keyError': 'Bill attachment required.'
        }
        if request.is_ajax():
            keyError = render_to_string(template4, context, request)
        return JsonResponse(
            {'keyError': keyError, })

    try:
        amount = Decimal(amt)
    except amt.InvalidOperation:
        print('aount', amount)
    print(amount, 'amount')
    exp_note = request.POST['exp_note']
    spender = request.user
    group_instance = Groups.objects.get(id=group_id)
    cal_period = CalculationPeriod.objects.get(group_id=group_instance, is_active=True)

    try:
        expensesAdded = Expenses.objects.create(group_id=group_instance, amount=amount, exp_note=exp_note,
                                                spender=spender, calculation_period=cal_period, bill=bill)
        print(expensesAdded, 'expensesAdeed')
        if expensesAdded:
            print('aaaaaaaaaaaaaaaa')

            group_expenses = Expenses.objects.filter(group_id=group_id, calculation_period=cal_period).order_by('-id')
            try:
                print('bbbbbbbbbbbbbbbbb')
                personal_t = PersonalTotal.objects.get(group_id=group_id, spender_id=request.user,
                                                       calculation_period=cal_period)
                print(personal_t.total_amount)
                peronal_total = personal_t.total_amount + amount
                print(peronal_total)
                personal_t.total_amount = peronal_total
                a = personal_t.save()
                print(a, 'bbcc')
                print('cccccccccccccccccccccccc')
                final_calculation(group_id)
                final_transaction = FinalTransaction.objects.filter(group_id=group_id, calculation_period=cal_period)
                owe = 0
                owned = 0
                for u in final_transaction:
                    print(u.to_user)
                    if u.to_user == request.user:
                        owned += u.amount
                    if u.from_user == request.user:
                        owe += u.amount

                print('ffffffffffffffffff', owe, owned)
                total_balance = owned - owe
                # total_exp(group_id)
            except PersonalTotal.DoesNotExist:
                print('dddddddddddddddddddd')
                PersonalTotal.objects.create(group_id=group_instance, total_amount=amount, spender_id=request.user,
                                             calculation_period=cal_period)
            print('eeeeeeeeeeeeeeeeee')
            membersEmail = group_instance.group_members.all()
            memEmail = []
            for me in membersEmail:
                if me.email != request.user.email:
                    memEmail.append(me.email)
            print(memEmail)
            domain = get_current_site(request).domain
            dashboard_link = 'http://' + domain + '/dashboard/'
            context = {
                'memberAdded': 'Expenses added ' + 'group_name' + '.',
                'expAdded': 'Added',
                'group_expenses': group_expenses,
                'final_transaction': final_transaction,
                'owe': owe,
                'owned': owned,
                'total_balance': total_balance,
                'group': group_instance,
                'user': request.user.first_name + ' ' + request.user.last_name,
                'dashboard_link': dashboard_link,
                'amount': amount,
                'exp_note': exp_note,
                'userEmail': request.user.email,
            }

            #     send email to new member
            email_subject = request.user.username + ' added ' + '$' + str(amount) + ' to the group ' + "'" + str(
                group_instance) + "'"
            html_message = render_to_string('email/addExpenses.html', context)
            plain_message = strip_tags(html_message)
            from_email = settings.EMAIL_HOST_USER
            to_email = memEmail

            email_body = plain_message

            send_email = EmailMultiAlternatives(
                email_subject,
                email_body,
                from_email,
                to_email,

            )
            send_email.attach_alternative(html_message, "text/html")
            EmailThread(send_email).start()

        else:
            context = {
                'memberAdded': 'Expenses NOT added ' + 'group_name' + '.',
                'expAdded': 'NotAdded',
            }
    except ValidationError:
        context = {
            'memberAdded': 'Amount must be a number. Do not include ''$'' sign.',
            'expAdded': 'NotAdded',
        }

    if request.is_ajax():
        html = render_to_string(template4, context, request=request)
        group_activities = render_to_string(template1, context, request=request)
        final_transaction = render_to_string(template2, context, request=request)
    return JsonResponse(
        {'post': html, 'Added': 'Added', 'group': group_activities, 'final_transaction': final_transaction})


def createCycle(request):
    template = 'groups/addedMessage.html'
    template1 = 'groups/GroupRecentActivities.html'
    template3 = 'groups/showGroupMemberNewCycle.html'
    if request.POST:
        print(request.POST)
        group_id = request.POST['groupName']
        group_instance = Groups.objects.get(id=group_id)
        try:
            old_calculation_period = CalculationPeriod.objects.get(group_id=group_instance, is_active=True)
            context = {
                'ActiveCalculationPeriod': 'Calculation period is active from: ' + str(
                    old_calculation_period.start_period) + '.',
                'memberIngroup': group_instance,
                'owe': 0,
                'owned': 0,
                'total_balance': 0,
                'SettleMessage': 'Calculation period already active.', }

        except CalculationPeriod.DoesNotExist:
            new_calculation_period = CalculationPeriod.objects.create(group_id=group_instance, is_active=True)
            if new_calculation_period:
                print('calculation')
                for x in group_instance.group_members.all():
                    print(x)
                    PersonalTotal.objects.create(group_id=group_instance, total_amount=0, spender_id=x,
                                                 calculation_period=new_calculation_period)
                domain = get_current_site(request).domain
                dashboard_link = 'http://' + domain + '/dashboard/'
                context = {
                    'ActiveCalculationPeriod': 'Calculation period is active from: ' + str(
                        new_calculation_period.start_period) + '.',
                    'memberIngroup': group_instance,
                    'cal_period': new_calculation_period,
                    'owe': 0,
                    'owned': 0,
                    'total_balance': 0,
                    'SettleMessage': 'New Calculation cycle is created. Now you CANNOT add or remove members form this group.',
                    # context for email
                    'group': group_instance,
                    'dashboard_link': dashboard_link,
                    'userEmail': request.user.email,
                    'user': request.user.first_name + ' ' + request.user.last_name,
                    'start_period': new_calculation_period.start_period,
                }
                # send email creating new calculation cycle.
                membersEmail = group_instance.group_members.all()
                memEmail = []
                for me in membersEmail:
                    if me.email != request.user.email:
                        memEmail.append(me.email)

                email_subject = request.user.username + ' created new cycle ' + ' of the group ' + "'" + str(
                    group_instance) + "'"
                html_message = render_to_string('email/startCycle.html', context)
                plain_message = strip_tags(html_message)
                from_email = settings.EMAIL_HOST_USER
                to_email = memEmail

                email_body = plain_message

                send_email = EmailMultiAlternatives(
                    email_subject,
                    email_body,
                    from_email,
                    to_email,

                )
                send_email.attach_alternative(html_message, "text/html")
                EmailThread(send_email).start()

    if request.is_ajax():
        html = render_to_string(template, context, request=request)
        group_activities = render_to_string(template1, context, request=request)
        groupMemberCycle = render_to_string(template3, context, request=request)
    return JsonResponse({'post': html, 'group_activities': group_activities, 'groupMemberCycle': groupMemberCycle})


def settleCycle(request):
    template = 'groups/addedMessage.html'
    template1 = 'groups/GroupRecentActivities.html'
    template3 = 'groups/showGroupMemberNewCycle.html'
    if request.POST:
        group_id = request.POST['groupName']
        group_instance = Groups.objects.get(id=group_id)
        old_calculation_period = CalculationPeriod.objects.get(group_id=group_instance, is_active=True)
        old_calculation_period.is_active = False
        old_calculation_period.end_period = datetime.now()
        old_calculation_period.save()
        print(old_calculation_period.is_active)
        is_active = old_calculation_period.is_active
        if not is_active:
            domain = get_current_site(request).domain
            dashboard_link = 'http://' + domain + '/dashboard/'
            final_transaction_email = FinalTransaction.objects.filter(calculation_period=old_calculation_period)
            print(final_transaction_email)
            print('----------------------------------------------------')
            context = {
                'ActiveCalculationPeriod': 'No active calculation period for this group.',
                'memberIngroup': group_instance,
                'owe': 0,
                'owned': 0,
                'total_balance': 0,
                'SettleMessage': 'Settled period cycle. Please refer to Final Calculation tab for calculations.',
                # context for email
                'group': group_instance,
                'dashboard_link': dashboard_link,
                'userEmail': request.user.email,
                'user': request.user.first_name + ' ' + request.user.last_name,
                'start_period': old_calculation_period.start_period,
                'end_period': old_calculation_period.end_period,
                'final_transaction_email': final_transaction_email,
            }
            # send email after settling calculation cycle.

            membersEmail = group_instance.group_members.all()
            memEmail = []
            for me in membersEmail:
                if me.email != request.user.email:
                    memEmail.append(me.email)

            email_subject = request.user.username + ' settled old cycle ' + ' of the group ' + "'" + str(
                group_instance) + "'"
            html_message = render_to_string('email/settleCycle.html', context)
            plain_message = strip_tags(html_message)
            from_email = settings.EMAIL_HOST_USER
            to_email = memEmail

            email_body = plain_message

            send_email = EmailMultiAlternatives(
                email_subject,
                email_body,
                from_email,
                to_email,

            )
            send_email.attach_alternative(html_message, "text/html")
            EmailThread(send_email).start()

    if request.is_ajax():
        html = render_to_string(template, context, request=request)
        group_activities = render_to_string(template1, context, request=request)
        groupMemberCycle = render_to_string(template3, context, request=request)
    return JsonResponse({'post': html, 'group_activities': group_activities, 'groupMemberCycle': groupMemberCycle})


def showPastTransactions(request):
    template = 'groups/pastTransactionDetails.html'
    selected_groups = Groups.objects.filter(group_members=request.user)
    cal_period = CalculationPeriod.objects.filter(group_id__in=selected_groups, is_active=False)
    # calculate total balance
    past_final_trans = FinalTransaction.objects.filter(calculation_period__in=cal_period)
    print('--------------------------000000000000-------------')
    for xy in past_final_trans:
        print(xy.calculation_period)
        print(xy.group_id)
    context = {
        'past_final_trans': past_final_trans,
        'selected_groups': selected_groups,
        'cal_period': cal_period,
    }
    if request.POST:
        if request.is_ajax():
            html = render_to_string(template, context, request=request)
        return JsonResponse({'post': html})


def final_transaction_sort(request):
    template = 'groups/dashboard.html'
    context = {}
    if request.POST:
        ft_id = request.POST['id']
        print(ft_id)
        ft = FinalTransaction.objects.get(id=ft_id).order_by('-id')
        ft.is_paid = True
        ft.save()
        print(ft)

    if request.is_ajax():
        html = render_to_string(template, context, request=request)
    return JsonResponse({'post': html})
