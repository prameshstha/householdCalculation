from django.contrib import admin
from .models import (CalculationPeriod, Expenses, Friends, FinalTransaction, Groups, TotalExpenses, PersonalTotal,
                     GroupType)
from accountUsers.models import accountUsers
from django.contrib.auth.admin import UserAdmin

# Register your models here.


admin.site.register(CalculationPeriod)
admin.site.register(Expenses)
admin.site.register(Friends)
admin.site.register(FinalTransaction)
admin.site.register(Groups)
admin.site.register(TotalExpenses)
admin.site.register(PersonalTotal)
admin.site.register(GroupType)


class UserAdmin(UserAdmin):
    list_display = ('id', 'email', 'username', 'date_joined', 'is_admin')
    search_fields = ('email', 'username')
    readonly_fields = ('date_joined', 'last_login')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(accountUsers, UserAdmin)
