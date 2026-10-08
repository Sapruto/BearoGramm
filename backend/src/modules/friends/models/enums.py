from enum import Enum


class FriendStatus(str, Enum):
    ACCEPT = "accept"
    REJECT = "rejected"
    PROCESS = "process"
    BLOCKED = "blocked"

    def __str__(self):
        return self.value
