import json
from django.conf import settings
from django.shortcuts import render, redirect
from .models import Profile, FriendRequest, FriendList, Player
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
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
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'error':'Username already exists'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'error':'email already exists'}, status=400)
        
        user = User.objects.create_user(username, email, password)
        return JsonResponse({'success': True, 'message':'Registration Successful', 'redirect':True, 'redirect_url': 'login'}, status=200)
    return render(request, 'user/register.html')
    # return JsonResponse({'success': False}, status=405)


def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                url = None
                if user.last_login == None:
                    url = 'profile-reg'
                else:
                    url = 'dashboard'
                return JsonResponse({'success': True, 'message': 'Login Successful', 'redirect': True, 'redirect_url': url}, status=200)
            else:
                return JsonResponse({'success': False, 'error': 'Account is disabled'})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid credentials'})
    
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return render(request, 'user/login.html')
    

@login_required
def dashboard_view(request):
    return render(request, 'user/dashboard.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def profile_view(request, *args, **kwargs):

    user_id = kwargs.get('user_id')
    try:
        account = User.objects.get(pk=user_id)
        # profile = Profile.objects.get(user=account.username)
    except:
        return JsonResponse({'success': False, 'message': 'User does not exist.'}, status=400)

    if account:
        data = {
            'username': account.username,
            'email': account.email,
            'first_name': account.first_name,
            'last_name': account.last_name,
            # 'avatar': profile.avatar.url,
            'last_login': account.last_login
        }

        is_self = True
        is_friend = False
        user = request.user

        if user.is_authenticated and user != account:
            is_self = False
        elif not user.is_authenticated:
            is_self = False
        
        data['is_self'] = is_self
        data['is_friend'] = is_friend
        
        context = {
            'json_data': json.dumps(data, cls=DjangoJSONEncoder)
        }
        return render(request, 'user/profile-view.html', context)



@login_required
def profile_viewr(request):
    user = request.user
    user_profile = User.objects.get(username=user)
    profile = Profile.objects.get(user=user)
    player = Player.objects.get(user=user)
    friends = FriendList.objects.filter(user=user)
    friends_list = [friend.friend.username for friend in friends]

    data = {
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'avatar': profile.avatar.url,
        'display_name': player.display_name,
        'friends': friends_list,
        'games_played': player.games_played,
        'wins': player.wins,
        'losses': player.losses,
        'is_active': user.is_active,
        'date_joined': user.date_joined,
        'last_login': user.last_login
    }

    # json_data = json.dumps(data, cls=DjangoJSONEncoder)

    # return JsonResponse(json_data, safe=False)
    return render(request, 'user/profile-view.html', {'data': data})



@login_required
def profile_reg(request):
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
            user.save()

        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=user)

        profile.avatar = avatar
        profile.save()

        player = Player.objects.create(user=user)
        
        return JsonResponse({'success': True, 'message': 'Profile Updated', 'redirect': True, 'redirect_url': 'profile'}, status=200)
    
    return render(request, 'user/profile-reg.html')

 

@login_required
def user_search_results(request):
    if request.method == 'POST':
        res = None
        entry = request.POST.get('userName')
        qs = User.objects.filter(username__icontains=entry)
        if len(qs) > 0 and len(entry) > 0:
            data = []
            for pos in qs:
                item = {
                    'pk': pos.pk,
                    'username': pos.username,
                    'first_name': pos.first_name,
                    'last_name': pos.last_name
                }
                data.append(item)
            res = data
        else:
            res = 'No results found...'

        return JsonResponse({'data': res})
    return JsonResponse({})


@login_required
def friend_request(request):
    pass



@login_required
def send_friend_request(request):
    user = request.user
    if request.method == 'POST':
        friend_id = request.POST.get('receiver_id')
        if friend_id:
            receiver = User.objects.get(pk=friend_id)
            try:
                friend_requests = FriendRequest.objects.filter(sender=user, receiver=receiver)
                try:
                    for req in friend_requests:
                        if req.is_active:
                            raise Exception("You have an active friend request.")
                    friend_request = FriendRequest(sender=user, receiver=receiver)
                    friend_request.save()
                    return JsonResponse({'success': True, 'message': 'Friend request was sent'}, status=200)
                except Exception as e:
                    return JsonResponse({'success': False, 'message': str(e)}, status=400)
            except FriendRequest.DoesNotExist:
                friend_request = FriendRequest(sender=user, receiver=receiver)
                friend_request.save()
                return JsonResponse({'success': True, 'message': 'Friend request was sent'}, status=200)
        else:
            return JsonResponse({'success': False, 'message': 'User does not exist'}, status=400)
    else:
        return JsonResponse({'success': False, 'message': 'method not allowed'}, status=403)