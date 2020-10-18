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
from django.urls import path
from .views import (index, test, my_profile,
                    create_group, dashboard, addMember, searchMembers, addFriendMember, getMemberOfGroup,
                    addExpenses, settleCycle, createCycle, showPastTransactions, final_transaction_sort,
                    edit_group, deleteMember, makeAdmin)

app_name = 'calculation'
urlpatterns = [
    path('', index, name='index'),
    path('test/', test, name='test'),
    path('my_profile/', my_profile, name='my_profile'),
    path('create_group/', create_group, name='create_group'),
    path('edit_group/<int:g_id>', edit_group, name='edit_group'),
    # path('save_group/', save_group, name='save_group'),
    path('dashboard/', dashboard, name='dashboard'),
    path('add_Member/', addMember, name='addMember'),
    path('deleteMember/', deleteMember, name='deleteMember'),
    path('makeAdmin/', makeAdmin, name='makeAdmin'),
    path('search_Members/', searchMembers, name='searchMembers'),
    path('addFriendMember/', addFriendMember, name='addFriendMember'),
    path('getMemberOfGroup/', getMemberOfGroup, name='getMemberOfGroup'),
    path('addExpenses/', addExpenses, name='addExpenses'),
    path('settleCycle/', settleCycle, name='settleCycle'),
    path('createCycle/', createCycle, name='createCycle'),
    path('showPastTransactions/', showPastTransactions, name='showPastTransactions'),
    path('final_transaction_sort/', final_transaction_sort, name='final_transaction_sort'),
]
