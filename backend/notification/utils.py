from django.core.serializers.python import Serializer
from django.contrib.humanize.templatetags.humanize import naturaltime


class LazyNotificationEncoder(Serializer):
	"""
	Serialize a Notification into JSON. 
	"""
	def get_dump_object(self, obj):
		dump_object = {}
		if obj.get_content_object_type() == "FriendRequest" or obj.get_content_object_type() == "GameRequest":
			dump_object.update({'notification_type': obj.get_content_object_type()})
			dump_object.update({'notification_id': str(obj.pk)})
			dump_object.update({'description': obj.description})
			dump_object.update({'is_active': str(obj.content_object.is_active)})
			dump_object.update({'is_read': str(obj.read)})
			dump_object.update({'natural_timestamp': str(naturaltime(obj.timestamp))})
			dump_object.update({'timestamp': str(obj.timestamp)})
			dump_object.update({
				'actions': {
					'redirect_url': str(obj.redirect_url).rstrip('/'),
				},
				"from": {
					"image_url": str(obj.from_user.avatar.url)
				}
			})
		if obj.get_content_object_type() == "FriendList":
			dump_object.update({'notification_type': obj.get_content_object_type()})
			dump_object.update({'notification_id': str(obj.pk)})
			dump_object.update({'description': obj.description})
			dump_object.update({'natural_timestamp': str(naturaltime(obj.timestamp))})
			dump_object.update({'is_read': str(obj.read)})
			dump_object.update({'timestamp': str(obj.timestamp)})
			dump_object.update({
				'actions': {
					'redirect_url': str(obj.redirect_url).rstrip('/'),
				},
				"from": {
					"image_url": str(obj.from_user.avatar.url)
				}
			})
		return dump_object