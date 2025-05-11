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

# Форма для редактирования одной регистрации
class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registrations
        fields = ['user', 'event', 'e_role_id', 'attendance']
        widgets = {
            'user': forms.Select(attrs={'readonly': True}),
            'event': forms.Select(attrs={'readonly': True}),
            'e_role_id': forms.Select(),
            'attendance': forms.CheckboxInput(),
        }

# Формсет — набор форм для всех записей
RegistrationFormSet = forms.modelformset_factory(
    Registrations,
    form=RegistrationForm,
    extra=0
)