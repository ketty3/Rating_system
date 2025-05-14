from django import forms
from .models import Profile,Events

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['middle_name', 'role', 'user_photo']
        #labels = {
            #'middle_name': 'Отчество',
            #'role': 'Роль',
            #'user_photo': 'Фото профиля',
        #}
class EventForm(forms.ModelForm):
    class Meta:
        model = Events
        fields = ['event_name', 'date', 'time', 'place', 'notes', 'available', 'event_photo']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

from .models import Registrations, EventRoles


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registrations
        fields = ['user', 'event', 'e_role_id', 'attendance']
        widgets = {
            'user': forms.HiddenInput(),
            'event': forms.HiddenInput(),
            'e_role_id': forms.Select(),
            'attendance': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убедимся, что поля user и event заполнены
        if self.instance:
            self.initial['user'] = self.instance.user
            self.initial['event'] = self.instance.event