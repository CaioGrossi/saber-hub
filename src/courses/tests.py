from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from courses.models import Course, CourseEnrollment, CoursePurchase


class CoursePricingAndPurchaseTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='prof.test',
            password='password123',
            role=User.Role.TEACHER,
            college='Universidade Teste',
        )
        self.student = User.objects.create_user(
            username='aluno.test',
            password='password123',
            role=User.Role.STUDENT,
            college='Universidade Teste',
        )
        self.course = Course.objects.create(
            teacher=self.teacher,
            title='Curso de Teste Python',
            description='Aprenda Python do zero.',
            price=Decimal('129.90'),
        )

    def test_teacher_can_create_course_with_price(self):
        self.client.login(username='prof.test', password='password123')
        response = self.client.post(
            reverse('create_course'),
            {
                'title': 'Novo Curso Django Avançado',
                'description': 'Ementa completa do curso avançado.',
                'price': '89.50',
            },
        )
        self.assertRedirects(response, reverse('course_list'))
        created = Course.objects.get(title='Novo Curso Django Avançado')
        self.assertEqual(created.price, Decimal('89.50'))
        self.assertEqual(created.teacher, self.teacher)

    def test_student_sees_price_and_buy_button_on_home(self):
        self.client.login(username='aluno.test', password='password123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'R$ 129.90')
        self.assertContains(response, reverse('purchase_course', args=[self.course.id]))

    def test_student_sees_price_on_course_detail(self):
        self.client.login(username='aluno.test', password='password123')
        response = self.client.get(reverse('student_course_detail', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'R$ 129.90')
        self.assertContains(response, reverse('purchase_course', args=[self.course.id]))

    def test_purchase_page_renders_for_student(self):
        self.client.login(username='aluno.test', password='password123')
        response = self.client.get(reverse('purchase_course', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '1111 1111 1111 1111')
        self.assertContains(response, '08/30')
        self.assertContains(response, '111')
        self.assertContains(response, 'R$ 129.90')

    def test_purchase_fails_with_invalid_card_details(self):
        self.client.login(username='aluno.test', password='password123')
        response = self.client.post(
            reverse('purchase_course', args=[self.course.id]),
            {
                'card_holder': 'ALUNO TESTE',
                'pan': '4111 1111 1111 1112',  # wrong PAN
                'expiration_date': '08/30',
                'cvv': '111',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CourseEnrollment.objects.filter(student=self.student, course=self.course).exists())
        self.assertFalse(CoursePurchase.objects.filter(student=self.student, course=self.course).exists())
        self.assertContains(response, 'Número de cartão inválido')

    def test_purchase_succeeds_with_valid_card_details(self):
        self.client.login(username='aluno.test', password='password123')
        response = self.client.post(
            reverse('purchase_course', args=[self.course.id]),
            {
                'card_holder': 'ALUNO TESTE',
                'pan': '1111 1111 1111 1111',
                'expiration_date': '08/30',
                'cvv': '111',
            },
            follow=True,
        )
        self.assertRedirects(response, reverse('student_course_detail', args=[self.course.id]))
        self.assertTrue(CourseEnrollment.objects.filter(student=self.student, course=self.course).exists())
        purchase = CoursePurchase.objects.get(student=self.student, course=self.course)
        self.assertEqual(purchase.amount, Decimal('129.90'))
        self.assertEqual(purchase.payment_method, 'credit_card')
        self.assertContains(response, 'Pagamento aprovado com sucesso')

    def test_already_enrolled_student_redirected_away_from_purchase(self):
        CourseEnrollment.objects.create(student=self.student, course=self.course)
        self.client.login(username='aluno.test', password='password123')
        response = self.client.get(reverse('purchase_course', args=[self.course.id]))
        self.assertRedirects(response, reverse('student_course_detail', args=[self.course.id]))

    def test_direct_enroll_redirects_to_purchase(self):
        self.client.login(username='aluno.test', password='password123')
        response = self.client.post(reverse('enroll_course', args=[self.course.id]))
        self.assertRedirects(response, reverse('purchase_course', args=[self.course.id]))

    def test_teacher_report_shows_revenue_and_sales(self):
        CoursePurchase.objects.create(
            student=self.student,
            course=self.course,
            amount=Decimal('129.90'),
            payment_method='credit_card',
        )
        self.client.login(username='prof.test', password='password123')
        response = self.client.get(reverse('teacher_report'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Total Faturado')
        self.assertContains(response, 'R$ 129.90')
        self.assertContains(response, 'Faturamento com Venda de Cursos')
        self.assertContains(response, '1 venda(s)')
