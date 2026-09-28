from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import redirect, render

from courses.models import Course, CourseEnrollment

from .forms import ProfileForm, RegisterForm
from .models import User


@login_required
def home(request):
    courses = None
    search_query = request.GET.get('q', '').strip()
    if request.user.role == User.Role.STUDENT:
        courses_queryset = Course.objects.select_related('teacher')
        if search_query:
            courses_queryset = courses_queryset.filter(title__icontains=search_query)

        courses = list(
            courses_queryset
            .annotate(
                total_materials=Count('materials', distinct=True),
                completed_materials_count=Count(
                    'materials__completions',
                    filter=Q(materials__completions__enrollment__student=request.user),
                    distinct=True,
                ),
            )
            .order_by('title'),
        )
        enrolled_course_ids = set(
            CourseEnrollment.objects.filter(student=request.user).values_list(
                'course_id',
                flat=True,
            ),
        )

        for course in courses:
            course.is_enrolled = course.id in enrolled_course_ids
            course.progress_percentage = 0
            if course.total_materials:
                course.progress_percentage = round(
                    (course.completed_materials_count / course.total_materials) * 100,
                )

    return render(
        request,
        'accounts/home.html',
        {
            'courses': courses,
            'search_query': search_query,
        },
    )


def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})
