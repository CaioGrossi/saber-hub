from django.contrib import admin

from .models import Certificate, CompletedMaterial, Course, CourseEnrollment, CourseMaterial


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher')
    search_fields = ('title', 'description', 'teacher__username')


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'url')
    search_fields = ('title', 'description', 'course__title')


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('student__username', 'student__email', 'course__title')


@admin.register(CompletedMaterial)
class CompletedMaterialAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'material', 'completed_at')
    list_filter = ('completed_at',)
    search_fields = (
        'enrollment__student__username',
        'enrollment__course__title',
        'material__title',
    )


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('student__username', 'student__email', 'course__title')
