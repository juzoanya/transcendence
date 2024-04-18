
def set_default_avatar():
    return 'avatars/default_avatar.png'


def get_avatar_path(self, filename):
    return f"avatars/{self.pk}/{'avatar.png'}"