from random import choice

class AvatarRandomizer:
    def __init__(self):
        self.avatars = ["default_avatar1", "default_avatar2", "default_avatar3", "default_avatar4"]

    def get_random_avatar(self):
        current_avatar = choice(self.avatars)
        current_avatar = "media/" + "default_avatars/" + current_avatar + ".png"
        return current_avatar
