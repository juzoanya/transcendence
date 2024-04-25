import json
from django.conf import settings
from django.shortcuts import render, redirect
from friends.models import FriendRequest, FriendList
from .models import UserAccount, Player
from friends.views import friend_list
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import default_storage
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

# def generate_jwt_token(user):
#     payload = {
#         'user_id': user.id,
#         'username': user.username,
#         'exp': datetime.utcnow() + timedelta(days=1)
#     }
#     return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')


def homepage(request):
	return render(request, 'index.html')


def register_view(request):
	user = request.user
	if user.is_authenticated:
		return JsonResponse({'success': True, 'message': f'You are already logged in as {user}'}, status=200)
	if request.method == 'POST':
		data = json.loads(request.body)
		username = data.get('username')
		email = data.get('email')
		password = data.get('password')

		if UserAccount.objects.filter(username=username).exists():
			return JsonResponse({'success': False, 'error':'Username already exists'}, status=400)
		if UserAccount.objects.filter(email=email).exists():
			return JsonResponse({'success': False, 'error':'email already exists'}, status=400)
		
		user = UserAccount.objects.create_user(username, email, password)
		return JsonResponse({'success': True, 'message':'Registration Successful'}, status=200)
	# return render(request, 'user/register.html')
	else:
		return JsonResponse({'success': False}, status=403)


def login_view(request):

	if request.user.is_authenticated:
		return JsonResponse({'success': True, 'message': 'You have an active session.'}, status=200)

	if request.method == 'POST':
		data = json.loads(request.body)
		username = data.get('username')
		password = data.get('password')

		user = authenticate(request, username=username, password=password)

		if user is not None:
			if user.is_active:
				login(request, user)
				user.status = 'online'
				user.save()
				return JsonResponse({'success': True, 'message': 'Login Successful'}, status=200)
			else:
				return JsonResponse({'success': False, 'error': 'Account is disabled'}, status=400)
		else:
			return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=400)
	else:
		return JsonResponse({'success': False}, status=403)   
	# return render(request, 'user/login.html')
	

@login_required
def check_full_profile(request):
	user = request.user
	account = UserAccount.objects.get(username=user)
	data = {
		'full_profile': account.full_profile
	}

	return JsonResponse({'data': data})



@login_required
def dashboard_view(request):
	return render(request, 'user/dashboard.html')


@login_required
def logout_view(request):
	user = request.user
	account = UserAccount.objects.get(username=user)
	try:
		logout(request)
		account.status = 'offline'
		account.save()
	except:
		return JsonResponse({'success': False, 'message': 'Something went wrong'}, status=500)
	return JsonResponse({'success': True, 'message': 'Logout successful'}, status=200)
	# return redirect('home')


@login_required
def profile_view(request, *args, **kwargs):

	user_id = kwargs.get('user_id')
	try:
		account = UserAccount.objects.get(pk=user_id)
	except:
		return JsonResponse({'success': False, 'message': 'User does not exist.'}, status=400)

	if account:
		data = {
			'id': account.pk,
			'username': account.username,
			'email': account.email,
			'first_name': account.first_name,
			'last_name': account.last_name,
			'avatar': account.avatar.url,
			'last_login': account.last_login,
			'date_joined': account.date_joined
		}

		is_self = True
		is_friend = False
		user = request.user

		if user.is_authenticated and user != account:
			is_self = False
		elif not user.is_authenticated:
			is_self = False
		
		friends = friend_list(request, *args, **kwargs)
		
		data['friends'] = friends
		data['is_self'] = is_self
		data['is_friend'] = is_friend
		
		context = {
			'json_data': json.dumps(data, cls=DjangoJSONEncoder)
		}
		return render(request, 'user/profile-view.html', context)


@login_required
def complete_profile(request):
	if request.method == 'POST':

		user = request.user
		first_name = request.POST.get('first_name')
		last_name = request.POST.get('last_name')

		avatar = None
		if 'avatar' in request.FILES:
			avatar = request.FILES['avatar']

		if first_name or last_name:
			if first_name:
				user.first_name = first_name
			if last_name:
				user.last_name = last_name
			if avatar:
				user.avatar = avatar
			user.save()
		
		user.full_profile = True
		user.save()
		player = Player.objects.create(user=user)
		
		return JsonResponse({'success': True, 'message': 'Profile Updated', 'redirect': True, 'redirect_url': 'profile'}, status=200)
	
	return render(request, 'user/profile-reg.html')

 

@login_required
def user_search_results(request):
	if request.method == 'POST':
		user = request.user
		res = None
		entry = request.POST.get('userName')
		search_results = UserAccount.objects.filter(username__icontains=entry)
		if len(search_results) > 0 and len(entry) > 0:
			data = []
			for account in search_results:
				item = {
					'id': account.pk,
					'username': account.username,
					'email': account.email,
					'first_name': account.first_name,
					'last_name': account.last_name,
					'avatar': account.avatar.url
				}
				user_friend_list = FriendList.objects.get(user=user)
				item['is_mutual_friend'] = user_friend_list.is_mutual_friend(account)
				data.append((item)) 
			res = data
		else:
			res = 'No results found...'

		return JsonResponse({'data': res})
	return JsonResponse({'success': False}, status=403)


@login_required
def search(request, *args, **kwargs):
	
	if request.method == 'GET':
		user = request.user
		query = request.GET.get('q')
		if len(query) > 0:
			search_results = UserAccount.objects.filter(username__icontains=query).filter(email__icontains=query).distinct()
			data = []
			for account in search_results:
				item = {
					'id': account.pk,
					'username': account.username,
					'email': account.email,
					'first_name': account.first_name,
					'last_name': account.last_name,
					'avatar': account.avatar.url
				}
				user_friend_list = FriendList.objects.get(user=user)
				data.append((item, user_friend_list.is_mutual_friend(account))) 
		return JsonResponse({'data': data})
	else:
		return JsonResponse({'success': False}, status=403)



