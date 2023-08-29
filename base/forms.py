from django.forms import ModelForm 
from .models import Room

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__' #gives all editable fields from Room model in form, can make list with attribute values 
        exclude = ['host', 'participants']