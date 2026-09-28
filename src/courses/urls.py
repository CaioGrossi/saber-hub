from django.urls import path

from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('create/', views.create_course, name='create_course'),
    path('enrolled/', views.enrolled_course_list, name='enrolled_course_list'),
    path('certificates/', views.certificate_list, name='certificate_list'),
    path('informes/professor/', views.teacher_report, name='teacher_report'),
    path('informes/student/', views.student_report, name='student_report'),
    path('<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('<int:course_id>/detail/', views.student_course_detail, name='student_course_detail'),
    path(
        '<int:course_id>/detail/material/<int:material_id>/',
        views.student_course_material_detail,
        name='student_course_material_detail',
    ),
    path(
        '<int:course_id>/detail/material/<int:material_id>/file/',
        views.student_course_material_file,
        name='student_course_material_file',
    ),
    path(
        '<int:course_id>/materials/<int:material_id>/toggle-completion/',
        views.toggle_material_completion,
        name='toggle_material_completion',
    ),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
]
