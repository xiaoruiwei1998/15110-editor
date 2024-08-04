from django.urls import path
from .views import *

app_name = 'student_api'

urlpatterns = [
    # Conversation/Chatlog related views
    path('/conversation', ConversationView.as_view(), name='conversation'),
    path('/conversation/all', ConversationListView.as_view(), name='conversation_list'),
    path('/conversation/history', ConversationHistoryView.as_view(), name='conversation_history'),
    path('/conversation/history/csv', ConversationHistoryCsvView.as_view(), name='conversation_history_csv'),
    path('/conversation/chatlog', ConversationChatlogsView.as_view(), name='conversation_history_list'),
    path('/conversation/end', ConversationEndView.as_view(), name='conversation_end'),
    
    path('/chatlog', ChatlogView.as_view(), name='chatlog'),
    path('/chatlog/all', ChatlogListView.as_view(), name='chatlog_list'),
    
]


