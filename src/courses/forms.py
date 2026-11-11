from django import forms

from .models import Course, CourseMaterial


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('title', 'description', 'price')
        labels = {
            'title': 'Titulo',
            'description': 'Descricao',
            'price': 'Preço (R$)',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'placeholder': '0.00'}),
        }


class CreditCardPurchaseForm(forms.Form):
    card_holder = forms.CharField(
        max_length=120,
        label='Nome do Titular',
        widget=forms.TextInput(attrs={
            'placeholder': 'Ex: MARIA S SILVA',
            'autocomplete': 'cc-name',
        }),
    )
    pan = forms.CharField(
        max_length=25,
        label='Número do Cartão (PAN)',
        widget=forms.TextInput(attrs={
            'placeholder': '1111 1111 1111 1111',
            'autocomplete': 'cc-number',
            'maxlength': '25',
        }),
    )
    expiration_date = forms.CharField(
        max_length=7,
        label='Data de Validade (MM/AA)',
        widget=forms.TextInput(attrs={
            'placeholder': '08/30',
            'autocomplete': 'cc-exp',
            'maxlength': '7',
        }),
    )
    cvv = forms.CharField(
        max_length=4,
        label='Código CVV',
        widget=forms.TextInput(attrs={
            'placeholder': '111',
            'autocomplete': 'cc-csc',
            'maxlength': '4',
        }),
    )

    def clean(self):
        cleaned_data = super().clean()
        pan = (cleaned_data.get('pan') or '').replace(' ', '').replace('-', '').strip()
        cvv = (cleaned_data.get('cvv') or '').strip()
        exp = (cleaned_data.get('expiration_date') or '').replace(' ', '').strip()

        errors = {}
        if pan != '1111111111111111':
            errors['pan'] = 'Número de cartão inválido. Use 1111 1111 1111 1111 para aprovar.'
        if cvv != '111':
            errors['cvv'] = 'CVV inválido. Use 111 para aprovar.'
        if exp not in ('08/30', '08/2030', '0830'):
            errors['expiration_date'] = 'Data inválida. Use 08/30 para aprovar.'

        if errors:
            for field, msg in errors.items():
                self.add_error(field, msg)
            raise forms.ValidationError(
                'Transação não autorizada. Verifique os dados do cartão de crédito informado. '
                'Para aprovação na simulação, utilize o cartão 1111 1111 1111 1111, CVV 111 e validade 08/30.'
            )

        return cleaned_data


class CourseMaterialForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial
        fields = ('title', 'description', 'url')
        labels = {
            'title': 'Titulo',
            'description': 'Descricao',
            'url': 'Arquivo do material',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_url(self):
        file = self.cleaned_data['url']
        if not file.name.lower().endswith(('.mp4', '.pdf')):
            raise forms.ValidationError('Envie apenas arquivos .mp4 ou .pdf.')
        return file
