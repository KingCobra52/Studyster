from django.contrib import admin

# Register your models here.
#models are registered to the admin panel 

from .models import Room, Topic, Message 

admin.site.register(Room) 
admin.site.register(Topic) 
admin.site.register(Message) 