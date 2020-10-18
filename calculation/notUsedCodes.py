#
# # from create group - after group created
# cal_period = CalculationPeriod.objects.create(is_active=True, group_id=created)
#                 # adding personal total expenses zero after adding member in a group.
#                 PersonalTotal.objects.create(group_id=created, total_amount=0, spender_id=request.user,
#                                              calculation_period=cal_period)
#
# # from add members - after adding members
#
# # adding personal total expenses zero after adding member in a group.
# cal_period = CalculationPeriod.objects.get(group_id=group, is_active=True)
# PersonalTotal.objects.create(group_id=group, total_amount=0, spender_id=member,
#                              calculation_period=cal_period)
#
# # from add friend member
# # adding personal total expenses zero after adding member in a group.
#         cal_period = CalculationPeriod.objects.get(group_id=group, is_active=True)
#         PersonalTotal.objects.create(group_id=group_name, total_amount=0, spender_id=friend_id,
#                                      calculation_period=cal_period)