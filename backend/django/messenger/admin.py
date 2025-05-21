from django.contrib import admin

# Register your models here.


from messenger.models import *

models_to_register = [
    Chat,
    User,
    ChatParticipant,
    Message,
    MessageRead
]


for model in models_to_register:
    admin.site.register(model)