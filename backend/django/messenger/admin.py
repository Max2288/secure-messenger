from django.contrib import admin
from messenger.models import *

# Register your models here.


models_to_register = [Chat, User, ChatParticipant, Message, MessageRead]


for model in models_to_register:
    admin.site.register(model)
