from decimal import Decimal
import mimetypes

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.http import FileResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.http import require_POST

from accounts.models import User

from .forms import CourseForm, CourseMaterialForm, CreditCardPurchaseForm
from .models import (
    Certificate,
    CompletedMaterial,
    Course,
    CourseEnrollment,
    CourseMaterial,
    CoursePurchase,
)


def teacher_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != User.Role.TEACHER:
            return HttpResponseForbidden('Apenas professores podem acessar esta pagina.')
        return view_func(request, *args, **kwargs)

    return wrapper


def student_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != User.Role.STUDENT:
            return HttpResponseForbidden('Apenas estudantes podem acessar esta pagina.')
        return view_func(request, *args, **kwargs)

    return wrapper


def create_certificate_if_course_completed(enrollment):
    total_materials = enrollment.course.materials.count()
    if total_materials == 0:
        return None

    completed_materials = enrollment.completed_materials.count()
    if completed_materials != total_materials:
        return None

    certificate, created = Certificate.objects.get_or_create(
        student=enrollment.student,
        course=enrollment.course,
    )
    if created:
        return certificate

    return None


@teacher_required
def course_list(request):
    search_query = request.GET.get('q', '').strip()
    courses = Course.objects.filter(teacher=request.user)
    if search_query:
        courses = courses.filter(title__icontains=search_query)
    courses = courses.order_by('title')

    return render(
        request,
        'courses/course_list.html',
        {
            'courses': courses,
            'search_query': search_query,
        },
    )


@student_required
def enrolled_course_list(request):
    search_query = request.GET.get('q', '').strip()
    courses_queryset = Course.objects.filter(enrollments__student=request.user)
    if search_query:
        courses_queryset = courses_queryset.filter(title__icontains=search_query)

    courses = list(
        courses_queryset
        .select_related('teacher')
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

    for course in courses:
        course.progress_percentage = 0
        if course.total_materials:
            course.progress_percentage = round(
                (course.completed_materials_count / course.total_materials) * 100,
            )

    return render(
        request,
        'courses/enrolled_course_list.html',
        {
            'courses': courses,
            'search_query': search_query,
        },
    )


@teacher_required
def teacher_report(request):
    course_rows = (
        Course.objects.filter(teacher=request.user)
        .annotate(
            enrolled_students=Count('enrollments__student', distinct=True),
            completed_students=Count('certificates__student', distinct=True),
            materials_count=Count('materials', distinct=True),
        )
        .order_by('-enrolled_students', '-completed_students', 'title')
    )
    enrollments = CourseEnrollment.objects.filter(course__teacher=request.user)
    certificates = Certificate.objects.filter(course__teacher=request.user)
    student_rows = (
        User.objects.filter(
            role=User.Role.STUDENT,
            certificates__course__teacher=request.user,
        )
        .annotate(completed_courses=Count('certificates__course', distinct=True))
        .order_by('-completed_courses', 'username')
    )

    # Financial / Sales metrics
    purchases_qs = CoursePurchase.objects.filter(course__teacher=request.user)
    total_revenue = purchases_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_sales_count = purchases_qs.count()
    average_ticket = (total_revenue / total_sales_count) if total_sales_count > 0 else Decimal('0.00')

    revenue_by_course = {
        item['course_id']: {
            'count': item['count'],
            'total': item['total'] or Decimal('0.00'),
        }
        for item in (
            purchases_qs
            .values('course_id')
            .annotate(total=Sum('amount'), count=Count('id'))
        )
    }

    recent_purchases = (
        purchases_qs
        .select_related('course', 'student')
        .order_by('-created_at')[:10]
    )

    attention_rows = []
    for course in course_rows:
        course.completion_rate = 0
        if course.enrolled_students:
            course.completion_rate = round(
                (course.completed_students / course.enrolled_students) * 100,
            )
        if course.enrolled_students and course.completion_rate < 50:
            attention_rows.append(course)

        rev_data = revenue_by_course.get(course.id, {'count': 0, 'total': Decimal('0.00')})
        course.sales_count = rev_data['count']
        course.total_revenue = rev_data['total']

    return render(
        request,
        'courses/teacher_report.html',
        {
            'attention_rows': attention_rows,
            'average_ticket': average_ticket,
            'completed_students_count': certificates.values('student').distinct().count(),
            'course_rows': course_rows,
            'recent_purchases': recent_purchases,
            'student_rows': student_rows,
            'total_certificates': certificates.count(),
            'total_courses': course_rows.count(),
            'total_enrollments': enrollments.count(),
            'total_revenue': total_revenue,
            'total_sales_count': total_sales_count,
            'total_students': enrollments.values('student').distinct().count(),
        },
    )


@student_required
def student_report(request):
    enrollment_rows = list(
        CourseEnrollment.objects.filter(student=request.user)
        .select_related('course', 'course__teacher')
        .annotate(
            total_materials=Count('course__materials', distinct=True),
            completed_materials_count=Count('completed_materials', distinct=True),
        )
        .order_by('course__title')
    )
    completed_course_ids = set(
        Certificate.objects.filter(student=request.user).values_list('course_id', flat=True),
    )

    for enrollment in enrollment_rows:
        enrollment.is_completed = enrollment.course_id in completed_course_ids
        enrollment.remaining_materials_count = max(
            enrollment.total_materials - enrollment.completed_materials_count,
            0,
        )
        enrollment.progress_percentage = 0
        if enrollment.total_materials:
            enrollment.progress_percentage = round(
                (enrollment.completed_materials_count / enrollment.total_materials) * 100,
            )

    next_course_rows = sorted(
        [enrollment for enrollment in enrollment_rows if not enrollment.is_completed],
        key=lambda enrollment: (
            -enrollment.progress_percentage,
            enrollment.remaining_materials_count,
            enrollment.course.title,
        ),
    )[:5]

    professor_rows = (
        User.objects.filter(
            role=User.Role.TEACHER,
            courses__enrollments__student=request.user,
        )
        .annotate(
            enrolled_courses=Count(
                'courses__enrollments',
                filter=Q(courses__enrollments__student=request.user),
                distinct=True,
            ),
            completed_courses=Count(
                'courses__certificates',
                filter=Q(courses__certificates__student=request.user),
                distinct=True,
            ),
        )
        .order_by('-enrolled_courses', '-completed_courses', 'username')
    )

    return render(
        request,
        'courses/student_report.html',
        {
            'completed_courses_count': len(completed_course_ids),
            'enrollment_rows': enrollment_rows,
            'in_progress_courses_count': max(len(enrollment_rows) - len(completed_course_ids), 0),
            'next_course_rows': next_course_rows,
            'professor_rows': professor_rows,
            'total_enrolled_courses': len(enrollment_rows),
        },
    )


@student_required
def certificate_list(request):
    certificates = (
        Certificate.objects.filter(student=request.user)
        .select_related('course', 'student')
        .order_by('-created_at')
    )

    return render(
        request,
        'courses/certificate_list.html',
        {'certificates': certificates},
    )


@student_required
def student_course_detail(request, course_id):
    course = get_object_or_404(
        Course.objects.select_related('teacher'),
        id=course_id,
    )
    enrollment = CourseEnrollment.objects.filter(
        student=request.user,
        course=course,
    ).first()
    materials = list(course.materials.order_by('id'))
    completed_material_ids = set()

    if enrollment:
        completed_material_ids = set(
            enrollment.completed_materials.values_list('material_id', flat=True),
        )

    total_materials = len(materials)
    completed_count = len(completed_material_ids)
    progress_percentage = 0
    if total_materials:
        progress_percentage = round((completed_count / total_materials) * 100)
    certificate = None
    if enrollment:
        certificate = Certificate.objects.filter(
            student=request.user,
            course=course,
        ).first()

    return render(
        request,
        'courses/student_course_detail.html',
        {
            'certificate': certificate,
            'course': course,
            'completed_count': completed_count,
            'completed_material_ids': completed_material_ids,
            'enrollment': enrollment,
            'materials': materials,
            'progress_percentage': progress_percentage,
            'total_materials': total_materials,
        },
    )


@student_required
def student_course_material_detail(request, course_id, material_id):
    course = get_object_or_404(
        Course.objects.select_related('teacher'),
        id=course_id,
    )
    material = get_object_or_404(CourseMaterial, id=material_id, course=course)
    enrollment = get_object_or_404(
        CourseEnrollment,
        student=request.user,
        course=course,
    )
    is_completed = CompletedMaterial.objects.filter(
        enrollment=enrollment,
        material=material,
    ).exists()
    file_name = material.url.name.lower()
    is_pdf = file_name.endswith('.pdf')
    is_video = file_name.endswith('.mp4')

    return render(
        request,
        'courses/student_course_material_detail.html',
        {
            'course': course,
            'enrollment': enrollment,
            'is_completed': is_completed,
            'is_pdf': is_pdf,
            'is_video': is_video,
            'material': material,
        },
    )


@student_required
@xframe_options_sameorigin
def student_course_material_file(request, course_id, material_id):
    course = get_object_or_404(Course, id=course_id)
    material = get_object_or_404(CourseMaterial, id=material_id, course=course)
    get_object_or_404(
        CourseEnrollment,
        student=request.user,
        course=course,
    )

    media_content_type, _ = mimetypes.guess_type(material.url.name)
    material_file = material.url.open('rb')
    return FileResponse(
        material_file,
        as_attachment=False,
        content_type=media_content_type or 'application/octet-stream',
        filename=material.url.name.rsplit('/', 1)[-1],
    )


@student_required
def purchase_course(request, course_id):
    course = get_object_or_404(
        Course.objects.select_related('teacher'),
        id=course_id,
    )

    if CourseEnrollment.objects.filter(student=request.user, course=course).exists():
        messages.info(request, 'Você já possui acesso a este curso.')
        return redirect('student_course_detail', course_id=course.id)

    if request.method == 'POST':
        form = CreditCardPurchaseForm(request.POST)
        if form.is_valid():
            CourseEnrollment.objects.get_or_create(
                student=request.user,
                course=course,
            )
            CoursePurchase.objects.create(
                student=request.user,
                course=course,
                amount=course.price,
                payment_method='credit_card',
            )
            messages.success(
                request,
                f'Pagamento aprovado com sucesso! Você adquiriu o curso "{course.title}". Bons estudos!',
            )
            return redirect('student_course_detail', course_id=course.id)
        else:
            messages.error(
                request,
                'Transação não autorizada. Verifique os dados do cartão informados.',
            )
    else:
        form = CreditCardPurchaseForm()

    return render(
        request,
        'courses/purchase_course.html',
        {
            'course': course,
            'form': form,
        },
    )


@student_required
@require_POST
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if CourseEnrollment.objects.filter(student=request.user, course=course).exists():
        messages.info(request, 'Você já está inscrito neste curso.')
        return redirect('student_course_detail', course_id=course.id)

    return redirect('purchase_course', course_id=course.id)


@student_required
@require_POST
def toggle_material_completion(request, course_id, material_id):
    course = get_object_or_404(Course, id=course_id)
    material = get_object_or_404(CourseMaterial, id=material_id, course=course)
    enrollment = get_object_or_404(
        CourseEnrollment,
        student=request.user,
        course=course,
    )
    completion, created = CompletedMaterial.objects.get_or_create(
        enrollment=enrollment,
        material=material,
    )

    if created:
        certificate = create_certificate_if_course_completed(enrollment)
        messages.success(request, 'Material marcado como concluido.')
        if certificate:
            messages.success(request, 'Certificado emitido com sucesso.')
    else:
        completion.delete()
        messages.success(request, 'Material marcado como pendente.')

    if request.POST.get('return_to') == 'material':
        return redirect(
            'student_course_material_detail',
            course_id=course.id,
            material_id=material.id,
        )

    return redirect('student_course_detail', course_id=course.id)


@teacher_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)

    if request.method == 'POST':
        form = CourseMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.course = course
            material.save()
            messages.success(request, 'Material adicionado com sucesso.')
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseMaterialForm()

    materials = course.materials.order_by('id')
    return render(
        request,
        'courses/course_detail.html',
        {
            'course': course,
            'materials': materials,
            'form': form,
        },
    )


@teacher_required
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            messages.success(request, 'Curso criado com sucesso.')
            return redirect('course_list')
    else:
        form = CourseForm()

    return render(request, 'courses/create_course.html', {'form': form})
