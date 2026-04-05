from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db import transaction
from .models import Account


@login_required
@csrf_exempt
def transferView(request):

	if request.method == 'POST':
		from_id = request.POST.get('from_id')
		to = request.POST.get('to')
		amount = int(request.POST.get('amount'))

		if from_id and to and amount:
			try:
				sender_acc = Account.objects.get(id=from_id)
    
				receiver = User.objects.get(username=to)
				receiver_acc = receiver.account
    
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
