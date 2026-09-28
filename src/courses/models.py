from django.conf import settings
from django.db import models


class Course(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses',
    )
    title = models.CharField(max_length=150)
    description = models.TextField()

    def __str__(self):
        return self.title


class CourseMaterial(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='materials',
    )
    title = models.CharField(max_length=150)
    description = models.TextField()
    url = models.FileField(upload_to='course_materials/')

    def __str__(self):
        return self.title


class CourseEnrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_enrollments',
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('student', 'course'),
                name='unique_student_course_enrollment',
            ),
        ]
        ordering = ('course__title',)

    def __str__(self):
        return f'{self.student} - {self.course}'


class CompletedMaterial(models.Model):
    enrollment = models.ForeignKey(
        CourseEnrollment,
        on_delete=models.CASCADE,
        related_name='completed_materials',
    )
    material = models.ForeignKey(
        CourseMaterial,
        on_delete=models.CASCADE,
        related_name='completions',
    )
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('enrollment', 'material'),
                name='unique_completed_material_per_enrollment',
            ),
        ]
        ordering = ('material__title',)

    def __str__(self):
        return f'{self.enrollment.student} - {self.material}'


class Certificate(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='certificates',
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='certificates',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('student', 'course'),
                name='unique_student_course_certificate',
            ),
        ]
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.student} - {self.course}'

    @property
    def display_text(self):
        student_name = self.student.get_full_name() or self.student.username
        date_text = self.created_at.strftime('%d/%m/%Y')
        return f'Estudante {student_name} concluiu o curso {self.course.title} no dia {date_text}.'
