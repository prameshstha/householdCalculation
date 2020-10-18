import decimal
import os

from datetime import datetime
from decimal import Decimal

from django.db import models
from django.db.models import Sum

from accountUsers.models import accountUsers


# Create your models here.


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_bill_image_path(instance, filename):
    group = instance.group_id
    print(instance, group, 'group')
    # print(instance)
    # print(filename)
    # new_filename = random.randint(1, 9999999999)
    new_filename = datetime.now()
    name, ext = get_filename_ext(filename)
    name = name[:5]
    final_filename = '{name}-{new_filename}{ext}'.format(new_filename=new_filename, ext=ext, name=name)
    print(new_filename, final_filename, name, ext, filename, instance)
    return 'images/groups/' + str(group) + '/bill/{final_filename}'.format(
        new_filename=new_filename,
        final_filename=final_filename
    )


def upload_pic_image_path(instance, filename):
    print(instance, 'group')
    # print(instance)
    # print(filename)
    # new_filename = random.randint(1, 9999999999)
    new_filename = datetime.now()
    name, ext = get_filename_ext(filename)
    name = name[:5]
    final_filename = '{name}-{new_filename}{ext}'.format(new_filename=new_filename, ext=ext, name=name)
    print(new_filename, final_filename, name, ext, filename, instance)
    return 'images/groups/' + str(instance) + '/pic/{final_filename}'.format(
        new_filename=new_filename,
        final_filename=final_filename
    )


class test(models.Model):
    image = models.ImageField(upload_to=upload_bill_image_path, null=True, blank=True)


class Groups(models.Model):
    group_admin = models.ForeignKey(accountUsers, on_delete=models.CASCADE, related_name='group_admin')
    group_pic = models.ImageField(upload_to=upload_pic_image_path, blank=True, null=True, )
    group_name = models.CharField(max_length=255)
    group_type = models.CharField(max_length=255)
    group_country = models.CharField(max_length=255)
    group_members = models.ManyToManyField(accountUsers, related_name='group_members', )
    group_created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.group_name)


class CalculationPeriod(models.Model):
    group_id = models.ForeignKey(Groups, on_delete=models.CASCADE, related_name='cal_group_id')
    start_period = models.DateField(auto_now_add=True)
    end_period = models.DateField(blank=True, null=True)
    per_head = models.CharField(max_length=255, blank=True, null=True)
    total_expenses = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField()

    def __str__(self):
        return str(self.id) + ' ' + str(self.group_id) + ' ' + str(self.start_period) + ' to ' + str(self.end_period)


class Expenses(models.Model):
    calculation_period = models.ForeignKey(CalculationPeriod, on_delete=models.CASCADE, related_name='cal_period',
                                           null=True)
    group_id = models.ForeignKey(Groups, on_delete=models.CASCADE, related_name='exp_group_id')
    spender = models.ForeignKey(accountUsers, on_delete=models.CASCADE, related_name='spender')
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bill = models.ImageField(upload_to=upload_bill_image_path, null=True, blank=True, )
    edited = models.DateTimeField(auto_now=True)
    added = models.DateTimeField(auto_now_add=True)
    exp_note = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return str(self.spender) + ' , ' + str(self.group_id)


class PersonalTotal(models.Model):
    calculation_period = models.ForeignKey(CalculationPeriod, on_delete=models.CASCADE,
                                           related_name='Personal_cal_period',
                                           null=True, blank=True)
    group_id = models.ForeignKey(Groups, on_delete=models.CASCADE, related_name='group_id_personal')
    spender_id = models.ForeignKey(accountUsers, on_delete=models.CASCADE, related_name='spender_id_personal')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return str(self.group_id) + ' , ' + str(self.spender_id) + ' , ' + str(self.total_amount)


class TotalExpenses(models.Model):
    calculation_period = models.ForeignKey(CalculationPeriod, on_delete=models.CASCADE, related_name='Total_cal_period',
                                           null=True)
    group_id = models.ForeignKey(Groups, on_delete=models.CASCADE, related_name='group_id_total')
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)


class FinalTransaction(models.Model):
    calculation_period = models.ForeignKey(CalculationPeriod, on_delete=models.CASCADE, related_name='final_cal_period', null=True, blank=True)
    from_user = models.ForeignKey(accountUsers, on_delete=models.CASCADE, related_name='from_user')
    to_user = models.ForeignKey(accountUsers, on_delete=models.CASCADE, related_name='to_user')
    group_id = models.ForeignKey(Groups, on_delete=models.CASCADE, related_name='group_id_final')
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return str(self.from_user) + ' to ' + str(self.to_user) + ' ' + str(self.amount)


class Friends(models.Model):
    user_id = models.ForeignKey(accountUsers, on_delete=models.CASCADE, related_name='user_id')
    friend_id = models.ManyToManyField(accountUsers, related_name='friend_id')
    creaded_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user_id)


def final_calculation(group_id):
    calculation_period = CalculationPeriod.objects.get(group_id=group_id, is_active=True)
    totals = PersonalTotal.objects.filter(group_id=group_id, calculation_period=calculation_period).aggregate(totalExpenses=Sum('total_amount'))
    totalExpenses = totals['totalExpenses']
    print(totalExpenses, 'ttttttttttttttttttttttttttttttttttttttttttt')
    ptAll = PersonalTotal.objects.filter(group_id=group_id, calculation_period=calculation_period)
    group_member_count = Groups.objects.get(id=group_id).group_members.count()
    print(group_member_count)
    perhead = (totalExpenses / group_member_count).quantize(Decimal("0.01"), decimal.ROUND_HALF_UP)  # converting long decimal to 2 decimal places

    all = []
    p = []
    n = []
    z = []
    for a in ptAll:
        print(a.spender_id, a.total_amount, )
        giveReceive = a.total_amount - perhead
        all.append({'name': a.spender_id, 'amount': a.total_amount, 'perhead': perhead,
                    'giveORreceive': giveReceive})
        if giveReceive > 0:
            p.append({'name': a.spender_id, 'amount': a.total_amount, 'perhead': perhead,
                      'giveORreceive': giveReceive})
        elif giveReceive < 0:
            n.append({'name': a.spender_id, 'amount': a.total_amount, 'perhead': perhead,
                      'giveORreceive': giveReceive})
        elif giveReceive == 0:
            z.append({'name': a.spender_id, 'amount': a.total_amount, 'perhead': perhead,
                      'giveORreceive': giveReceive})

    print(len(all))
    print('all', all)
    print('----------------------------------------------')
    print('positive', p)
    print('----------------------------------------------')
    PdataSorted = sorted(p, key=lambda k: k['giveORreceive'], reverse=True)
    print('sorted positive', PdataSorted)
    print('----------------------------------------------')
    print('negative', n)
    print('----------------------------------------------')
    NdataSorted = sorted(n, key=lambda k: k['giveORreceive'])
    print('sorted negative', NdataSorted)
    print('----------------------------------------------')
    print('zero', z)

    # print(all[0]['perhead'], 'name', perhead.quantize(Decimal("0.01"), decimal.ROUND_HALF_UP))
    # calculation part
    # start copied js to edit

    finalData = []  # initializing new array for calculated value
    count = 0
    j = 0
    if count < len(NdataSorted):
        while j < len(NdataSorted):
            print(count, j, 'initial', len(PdataSorted), NdataSorted)
            if count < len(PdataSorted):
                toReceive = PdataSorted[count]['giveORreceive']
                # toReceive =tReceive
                print(toReceive, 'receiver')

                toGive = NdataSorted[j]['giveORreceive']  # retrieve form key of first index
                print(toGive, 'giver')
                # var receiver_Balance = +toReceive + +toGive;
                absGiver = abs(toGive)
                print(absGiver, 'abs giver value')
                print(NdataSorted[j]['giveORreceive'], 'giver')

                # checking if giver is greater than receiver in absolute value
                if absGiver > toReceive:
                    receiver_Balance = absGiver - toReceive
                    # adding value to dictionary
                    finalData.append({
                        'FromName': NdataSorted[j]['name'],
                        'toName': PdataSorted[count]['name'],
                        'amount': toReceive,
                    })
                    # receiver will be zero and giver will be absGiver - toReceive
                    # update the both NdataSorted and PdataSorted with above value
                    PdataSorted[count]['giveORreceive'] = 0
                    # delete PdataSorted[count];
                    toGive = (toReceive - absGiver)
                    print(toGive, 'new give')
                    toReceive = 0
                    print(PdataSorted)
                    print(finalData)
                    count += 1
                    print(count, 'last')
                    NdataSorted[j]['giveORreceive'] = toGive
                    print(NdataSorted)

                    j = j - 1
                    print(j, 'j')
                else:
                    dis = (+toReceive + +toGive)
                    # adding value to dictionary
                    finalData.append({
                        'FromName': NdataSorted[j]['name'],
                        'toName': PdataSorted[count]['name'],
                        'amount': absGiver,
                    })
                    # giver will be zero and receiver will be + toReceive + +toGive
                    # update the both NdataSorted and PdataSorted with above value

                    toReceive = dis
                    print(toReceive, 'new rece')
                    # delete NdataSorted[i];
                    if toReceive > 0:
                        print(j)
                        PdataSorted[count]['giveORreceive'] = dis
                        print('no property')
                    print(finalData)
                    print('final Data')
                    print(len(PdataSorted), len(NdataSorted), count)
                    # printfun(finalData)
                    print('final Data11')

                    if toReceive <= 0:
                        count += 1
            j = j + 1
    # print(finalData[0]['FromName'].username)
    group_instance = Groups.objects.get(id=group_id)
    ft = FinalTransaction.objects.filter(group_id=group_id, calculation_period=calculation_period).delete()
    if ft:
        for x in finalData:
            print(x['FromName'],  x['toName'].username, x['amount'])
            from_user = x['FromName']
            to_user = x['toName']
            amountToClear = x['amount']
            FinalTransaction.objects.create(from_user=from_user, to_user=to_user, group_id=group_instance, amount=amountToClear, calculation_period=calculation_period)

    # end copied js to edit

    return FinalTransaction


class GroupType(models.Model):
    group_type = models.CharField(max_length=255)

    def __str__(self):
        return str(self.group_type)

