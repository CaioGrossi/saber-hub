from django import forms

from .models import Course, CourseMaterial


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('title', 'description')
        labels = {
            'title': 'Titulo',
            'description': 'Descricao',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }


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
