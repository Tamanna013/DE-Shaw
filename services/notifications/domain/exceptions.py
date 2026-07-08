class NotificationError(Exception):
    pass

class InvalidChannelPreferenceError(NotificationError):
    pass

class DuplicateNotificationError(NotificationError):
    pass
