class FriendError(Exception):
    pass


class InvalidTargetIdentifier(FriendError):
    def __init__(self, target_value: str):
        self.target_value = target_value
        super().__init__(f"Cannot resolve target: {target_value}")


class CannotBeFriendWithSelf(FriendError):
    def __init__(self):
        super().__init__("You can't be friends with yourself")


class CannotBlockYourself(FriendError):
    def __init__(self):
        super().__init__("You can't block yourself")


class FriendshipAlreadyExists(FriendError):
    def __init__(self, user_uuid1: str, user_uuid2: str):
        self.user_uuid1 = user_uuid1
        self.user_uuid2 = user_uuid2
        super().__init__(f"Friendship between {user_uuid1} and {user_uuid2} already exists")


class FriendRequestNotFound(FriendError):
    def __init__(self, user_uuid1: str, user_uuid2: str):
        self.user_uuid1 = user_uuid1
        self.user_uuid2 = user_uuid2
        super().__init__(f"Friend request between {user_uuid1} and {user_uuid2} not found")


class FriendRequestAlreadyHandled(FriendError):
    def __init__(self, status: str):
        self.status = status
        super().__init__(f"Friend request already handled with status: {status}")


class CannotAcceptOwnRequest(FriendError):
    def __init__(self):
        super().__init__("You can't accept your own friend request")


class CannotRejectOwnRequest(FriendError):
    def __init__(self):
        super().__init__("You can't reject your own friend request")


class UserAlreadyBlocked(FriendError):
    def __init__(self, user_uuid1: str, user_uuid2: str):
        self.user_uuid1 = user_uuid1
        self.user_uuid2 = user_uuid2
        super().__init__(f"User {user_uuid2} already blocked by {user_uuid1}")


class UserNotBlocked(FriendError):
    def __init__(self, user_uuid1: str, user_uuid2: str):
        self.user_uuid1 = user_uuid1
        self.user_uuid2 = user_uuid2
        super().__init__(f"User {user_uuid2} is not blocked by {user_uuid1}")


class NotFriends(FriendError):
    def __init__(self, user_uuid1: str, user_uuid2: str):
        self.user_uuid1 = user_uuid1
        self.user_uuid2 = user_uuid2
        super().__init__(f"Users {user_uuid1} and {user_uuid2} are not friends")
