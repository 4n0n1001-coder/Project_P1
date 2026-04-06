from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.db import transaction
from .models import Account
from django.db import connection
from django.contrib.auth.hashers import check_password, make_password


# FIX: Fixed IDOR-vulnerability
# Instead of creating a request.POST.get('from_id'),
# we use directly the login account (request.user).
# This way money can be transferred only from current user.



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
				# Business Logic / Access Control
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


@login_required
def homePageView(request):
	accounts = Account.objects.exclude(user_id=request.user.id)
	return render(request, 'pages/index.html', {'accounts': accounts})
	

# 
@csrf_exempt
def Login(request):
	if request.method == 'POST':
		user = request.POST.get('username')
		passwd = request.POST.get('password')
        
		sql = f"SELECT id, password FROM auth_user WHERE username='{user}';"

		with connection.cursor() as cursor:
			cursor.execute(sql)
			row = cursor.fetchall()
        
		if row:
			row = row[0]
			id = row[0]
			hashed_password = row[1]
				
   
			if check_password(passwd, hashed_password):
				user_obj = User.objects.get(id=id)
				login(request, user_obj)
				return redirect('/')
		else:
			return render(request, 'pages/login.html', {'error': 'Please enter a correct username and password. Note that both fields may be case-sensitive.'})

	return render(request, 'pages/login.html')
