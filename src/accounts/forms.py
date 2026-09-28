from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


NO_COLLEGE = 'No college'
COLLEGE_HAS_COLLEGE = 'has_college'
COLLEGE_NO_COLLEGE = 'no_college'
NO_COLLEGE_LABEL = 'Sem faculdade'


class CollegeFieldsMixin(forms.Form):
    college_choice = forms.ChoiceField(
        choices=(
            (COLLEGE_HAS_COLLEGE, 'Estudo em uma faculdade'),
            (COLLEGE_NO_COLLEGE, NO_COLLEGE_LABEL),
        ),
        label='Faculdade',
        widget=forms.Select(attrs={'class': 'select-field'}),
    )
    college = forms.CharField(
        label='Nome da faculdade',
        max_length=150,
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        college_choice = cleaned_data.get('college_choice')
        college = (cleaned_data.get('college') or '').strip()

        if college_choice == COLLEGE_HAS_COLLEGE and not college:
            self.add_error('college', 'Informe o nome da faculdade ou escolha Sem faculdade.')

        cleaned_data['college'] = NO_COLLEGE if college_choice == COLLEGE_NO_COLLEGE else college
        return cleaned_data


class RegisterForm(CollegeFieldsMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'role', 'college_choice', 'college')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].widget.attrs.update({'class': 'select-field'})


class ProfileForm(CollegeFieldsMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'college_choice', 'college')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.college == NO_COLLEGE:
            self.fields['college_choice'].initial = COLLEGE_NO_COLLEGE
            self.fields['college'].initial = ''
        else:
            self.fields['college_choice'].initial = COLLEGE_HAS_COLLEGE
