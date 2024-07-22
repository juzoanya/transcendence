DEFAULT_NOTIFICATION_PAGE_SIZE = 10

GENERAL_MSG_TYPE_NOTIFICATIONS_DATA = 0  # New 'general' notifications data payload incoming
GENERAL_MSG_TYPE_PAGINATION_EXHAUSTED = 1  # No more 'general' notifications to retrieve
GENERAL_MSG_TYPE_NOTIFICATIONS_REFRESH_PAYLOAD = 2  # Retrieved all 'general' notifications newer than the oldest visible on screen
GENERAL_MSG_TYPE_UPDATED_NOTIFICATION = 5 # Update a notification that has been altered
