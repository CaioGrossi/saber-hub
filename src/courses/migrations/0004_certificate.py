from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def create_certificates_for_completed_courses(apps, schema_editor):
    CourseEnrollment = apps.get_model('courses', 'CourseEnrollment')
    Certificate = apps.get_model('courses', 'Certificate')

    for enrollment in CourseEnrollment.objects.all().iterator():
        total_materials = enrollment.course.materials.count()
        if total_materials == 0:
            continue

        completed_materials = enrollment.completed_materials.count()
        if completed_materials == total_materials:
            Certificate.objects.get_or_create(
                student_id=enrollment.student_id,
                course_id=enrollment.course_id,
            )


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_courseenrollment_completedmaterial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certificates', to='courses.course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certificates', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.AddConstraint(
            model_name='certificate',
            constraint=models.UniqueConstraint(fields=('student', 'course'), name='unique_student_course_certificate'),
        ),
        migrations.RunPython(
            create_certificates_for_completed_courses,
            migrations.RunPython.noop,
        ),
    ]
