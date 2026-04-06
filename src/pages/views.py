from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.db import transaction
from .models import Account
from django.db import connection


# [1] Insecure Direct Object Reference
# FIX: Fixed IDOR-vulnerability
# Instead of creating a request.POST.get('from_id'),
# we use directly the login account (request.user).
# This way money can be transferred only from current user.
#
# [3] Security missconfiguration
# PoC 
'''fetch('/transfer/', {
  method: 'POST',
  body: new URLSearchParams({
    'from_id': '2',
    'to': 'alice',
    'amount': '10'
  })
}).then(() => window.location.reload());
'''
#
#
# [4] Business Logic Error
# User is able to create money from nothing by doubling the
# sum of bank account by sending the money for him self.
@login_required
@csrf_exempt
def transferView(request):

	if request.method == 'POST':
		# Vulnerability 1: IDOR (Insecure Directy Object Reference)
		# currently taking sender ID directly send data from the browser
		from_id = request.POST.get('from_id')
  
  
		# ---- FIX ---- 
		# Insecure Directory Object Reference
		# To fix this, from_id is no longer used and it should be replaced with
		#sender_acc = request.user.account
  		# and sender_acc = Account.objects.get(id=from_id) should not be existsing no longer.
		# -------------
  
		to = request.POST.get('to')
		amount = int(request.POST.get('amount'))

		if from_id and to and amount:
			try:
				
				sender_acc = Account.objects.get(id=from_id)
    
				receiver = User.objects.get(username=to)
				receiver_acc = receiver.account
    
				# ---- FIX ----
				# [4] Business Logic / Access Control
				# Validate that the sender is not same as receiver
				# if sender_acc.balance >= amount and sender_acc != receiver_acc:
				# -------------
				if sender_acc.balance >= amount:
					sender_acc.balance -= amount
					receiver_acc.balance += amount
     
					sender_acc.save()
					receiver_acc.save()
			except (User.DoesNotExist, Account.DoesNotExist, ValueError):
				pass

	return redirect('/')

@csrf_exempt
@login_required
def homePageView(request):
	accounts = Account.objects.exclude(user_id=request.user.id)
	return render(request, 'pages/index.html', {'accounts': accounts})
	

# A1:2017-Injection
# SQL-Injection - PoC
#   Username inputfield is vulnerable for SQL injection
#	1. Inject simple sql code to inputfield
#	  F.ex: username: bob' -- 
#			password: what_ever_you_want_but_not_plank
#
# ---- FIX ---- 
# [2] SQL injection
# Use instead of Django internal auth LoginView framework.
# Replace current Login method in config/urls.py file and replace with below method
# path('login/', LoginView.as_view(template_name='pages/login.html')),
# and consider below Login functions as expired.
# -------------
@csrf_exempt
def Login(request):
	if request.method == 'POST':
		user = request.POST.get('username')
		passwd = request.POST.get('password')
        
		sql = f"SELECT id, password FROM auth_user WHERE username='{user}' AND password='{passwd}';"

		with connection.cursor() as cursor:
			cursor.execute(sql)
			credentials = cursor.fetchall()
        
		if credentials:
			credentials = credentials[0]
			_id = credentials[0]
			user_obj = User.objects.get(id=_id)
			
			login(request, user_obj)
			return redirect('/')
		else:
			return render(request, 'pages/login.html', {'error': 'Please enter a correct username and password. Note that both fields may be case-sensitive.'})

	return render(request, 'pages/login.html')



# [1] A5:2017-Broken Access Control
# [2] A1:2017-Injection
# [3] A6:2016-Security Missconfiguration 
# [4] A5:2017-Business logic Error