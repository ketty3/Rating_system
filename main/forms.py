from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['middle_name', 'role', 'user_photo']
        #labels = {
            #'middle_name': 'Отчество',
            #'role': 'Роль',
            #'user_photo': 'Фото профиля',
        #}
