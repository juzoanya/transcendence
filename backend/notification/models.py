from django.db import models
from user.models import UserAccount
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Create your models here.


class Notification(models.Model):
    target = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    from_user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, null=True, blank=True, related_name='from_user')
    redirect_url = models.URLField(max_length=500, unique=False, null=True, blank=True, help_text="redirection for when the notification is clicked")
    description = models.CharField(max_length=255, unique=False, blank=True, null=True)
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __str__(self):
        return self.description
    
    def get_content_object_type(self):
        return str(self.content_object.get_cname)
    
