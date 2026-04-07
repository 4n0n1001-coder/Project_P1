from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.db import transaction
from .models import Account
from django.db import connection


# [FLAW 3/4] Insecure Direct Object Reference & Business Logic Error
@login_required
@csrf_exempt
def transferView(request):

	if request.method == 'POST':
		
		# [FLAW 3] Taking the sender ID directly from the browser
		from_id = request.POST.get('from_id')
  
  
		# [FIX 3]
		# Instead pick the ID from user account
  		#sender_acc = request.user.account
		
		to = request.POST.get('to')
		amount = int(request.POST.get('amount'))

		if from_id and to and amount:
			try:
				
				sender_acc = Account.objects.get(id=from_id)
    
				receiver = User.objects.get(username=to)
				receiver_acc = receiver.account
    
				# [FLAW 4] 
				# Nothing validate that the sender is not the same as receiver
				if sender_acc.balance >= amount:
        
				# [FIX 4]
				# Add validation to the statement to check that the
				# sender is not the same person as the receiver
    			#if sender_acc.balance >= amount and sender_acc != receiver_acc:
        
					sender_acc.balance -= amount
					receiver_acc.balance += amount
     
					sender_acc.save()
					receiver_acc.save()
			except (User.DoesNotExist, Account.DoesNotExist, ValueError):
				pass

	return redirect('/')


# [FLAW 6] homePageView is vulnerable for Cross-Site Scripting (XSS)
# The 'name' parameter is taken directly from the URL and passed to the template.
@csrf_exempt
@login_required
def homePageView(request):
	name = request.GET.get('name', request.user.username)
	accounts = Account.objects.exclude(user_id=request.user.id)
	return render(request, 'pages/index.html', {'accounts': accounts, 'name': name})

	# [FIX 6]
	# The fix is mainly in the template (index.html), but we could also
	# remove the unnecessary 'name' parameter if it's not needed
	#accounts = Account.objects.exclude(user_id=request.user.id)
	#return render(request, 'pages/index.html', {'accounts': accounts})
	

# [FLAW 1] Vulnerable login function
@csrf_exempt
def Login(request):
	if request.method == 'POST':
		user = request.POST.get('username')
		passwd = request.POST.get('password')
        
        # [FLAW 1] SQL-injection vulnerability
        # password matching is easy to skip and login without
        # knowing the password.
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

# [FIX 1] The correct way to do this is to use Django views.
# The above login function can be removed completely, and Django's internal LoginView object
# can be used instead. It can be found in the file config/urls.py. It will authenticate safely
# and is not vulnerable to SQL injections.
# To get this to work, the database requires hashed passwords, because Django's internal LoginView won't
# match against plaintext passwords for security reasons.

