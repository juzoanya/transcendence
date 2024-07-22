from .models import *
from user.utils import *
from django.db.models import Q, Count


def get_private_room_or_create(user1, user2):
    # alternate_title = '-'.join(title.split('-')[::-1])
    try:
        # room = ChatRoom.objects.get(Q(users=user1) & Q(users=user2), type='private')
        room = ChatRoom.objects.annotate(num_users=Count('users')).filter(
            users=user1
        ).filter(users=user2).filter(
            num_users=2,
            type='private'
        ).get()
    except ChatRoom.DoesNotExist:
        # from friends.models import FriendList
        # try:
        #     friend_list = FriendList.objects.get(user=user1)
        # except Exception as e:
        #     InternalServerError500(message=str(e))
        # if not friend_list.is_mutual_friend(user2):
        #     return None
        room = check_private_room_by_title(str(user1) + '.' + str(user2))
        if room == None:
            try:
                room = ChatRoom.objects.create(
                    title = str(user1.username + '.' + user2.username),
                    type='private'
                )
                room.users.add(user1)
                room.users.add(user2)
                room.save()
                print(f'--->>> get_private_room created')
            except Exception as e:
                raise InternalServerError500(message=str(e))
    return room

def check_private_room_by_title(title):
    try:
        room = ChatRoom.objects.get(title=title)
        return room
    except ChatRoom.DoesNotExist:
        try:
            room = ChatRoom.objects.get(title='-'.join(title.split('.')[::-1]))
            return room
        except ChatRoom.DoesNotExist:
            return None
