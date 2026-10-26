from django.core.management.base import BaseCommand
from accounts.models import User
from courses.models import (
    Course,
    CourseMaterial,
    CourseEnrollment,
    CompletedMaterial,
    Certificate,
)


class Command(BaseCommand):
    help = 'Popula o banco de dados com professores, estudantes, cursos, materiais e inscrições.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Iniciando o povoamento do banco de dados...'))

        default_password = 'senha123'

        # 1. Professores
        teachers_data = [
            {
                'username': 'grossi',
                'first_name': 'Caio',
                'last_name': 'Grossi',
                'email': 'caio.grossi@saberhub.com',
                'college': 'Universidade Federal de Santa Catarina (UFSC)',
            },
            {
                'username': 'prof.ana',
                'first_name': 'Ana',
                'last_name': 'Silva',
                'email': 'ana.silva@usp.br',
                'college': 'Universidade de São Paulo (USP)',
            },
            {
                'username': 'prof.carlos',
                'first_name': 'Carlos',
                'last_name': 'Eduardo',
                'email': 'carlos.eduardo@unicamp.br',
                'college': 'Universidade Estadual de Campinas (UNICAMP)',
            },
            {
                'username': 'prof.mariana',
                'first_name': 'Mariana',
                'last_name': 'Costa',
                'email': 'mariana.costa@ufmg.br',
                'college': 'Universidade Federal de Minas Gerais (UFMG)',
            },
            {
                'username': 'prof.roberto',
                'first_name': 'Roberto',
                'last_name': 'Santos',
                'email': 'roberto.santos@puc-rio.br',
                'college': 'PUC-Rio',
            },
        ]

        teachers = {}
        for t_info in teachers_data:
            user, created = User.objects.get_or_create(
                username=t_info['username'],
                defaults={
                    'first_name': t_info['first_name'],
                    'last_name': t_info['last_name'],
                    'email': t_info['email'],
                    'role': User.Role.TEACHER,
                    'college': t_info['college'],
                },
            )
            if created:
                user.set_password(default_password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Professor criado: {user.username} ({user.get_full_name()})"))
            else:
                user.first_name = t_info['first_name']
                user.last_name = t_info['last_name']
                user.email = t_info['email']
                user.role = User.Role.TEACHER
                user.college = t_info['college']
                user.save()
                self.stdout.write(f"Professor atualizado: {user.username}")
            teachers[user.username] = user

        # 2. Estudantes
        students_data = [
            {
                'username': 'aluno.lucas',
                'first_name': 'Lucas',
                'last_name': 'Oliveira',
                'email': 'lucas.oliveira@usp.br',
                'college': 'Universidade de São Paulo (USP)',
            },
            {
                'username': 'aluna.beatriz',
                'first_name': 'Beatriz',
                'last_name': 'Lima',
                'email': 'beatriz.lima@unicamp.br',
                'college': 'Universidade Estadual de Campinas (UNICAMP)',
            },
            {
                'username': 'aluno.gabriel',
                'first_name': 'Gabriel',
                'last_name': 'Souza',
                'email': 'gabriel.souza@ufmg.br',
                'college': 'Universidade Federal de Minas Gerais (UFMG)',
            },
            {
                'username': 'aluna.camila',
                'first_name': 'Camila',
                'last_name': 'Ferreira',
                'email': 'camila.ferreira@puc-rio.br',
                'college': 'PUC-Rio',
            },
            {
                'username': 'aluno.pedro',
                'first_name': 'Pedro',
                'last_name': 'Henrique',
                'email': 'pedro.henrique@gmail.com',
                'college': 'No college',
            },
        ]

        students = {}
        for s_info in students_data:
            user, created = User.objects.get_or_create(
                username=s_info['username'],
                defaults={
                    'first_name': s_info['first_name'],
                    'last_name': s_info['last_name'],
                    'email': s_info['email'],
                    'role': User.Role.STUDENT,
                    'college': s_info['college'],
                },
            )
            if created:
                user.set_password(default_password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Estudante criado: {user.username} ({user.get_full_name()})"))
            else:
                user.first_name = s_info['first_name']
                user.last_name = s_info['last_name']
                user.email = s_info['email']
                user.role = User.Role.STUDENT
                user.college = s_info['college']
                user.save()
                self.stdout.write(f"Estudante atualizado: {user.username}")
            students[user.username] = user

        # 3. Cursos e Materiais
        courses_data = [
            {
                'teacher_username': 'prof.ana',
                'title': 'Inteligência Artificial e Machine Learning',
                'description': 'Introdução aos fundamentos da Inteligência Artificial, modelos de aprendizado de máquina supervisionado e não supervisionado, redes neurais e considerações éticas em sistemas modernos.',
                'materials': [
                    {
                        'title': 'Fundamentos da Inteligência Artificial',
                        'description': 'Conceitos básicos, história da IA, algoritmos de busca e raciocínio lógico.',
                        'url': 'course_materials/1_fundamentos_da_ia.pdf',
                    },
                    {
                        'title': 'Aprendizado de Máquina na Prática',
                        'description': 'Regressão, classificação, árvores de decisão e métricas de avaliação de modelos.',
                        'url': 'course_materials/1_aprendizado_de_maquina.pdf',
                    },
                    {
                        'title': 'Ética em Sistemas Inteligentes',
                        'description': 'Vieses algorítmicos, transparência, privacidade e o impacto social da IA.',
                        'url': 'course_materials/1_etica_em_sistemas_inteligentes.pdf',
                    },
                ],
            },
            {
                'teacher_username': 'grossi',
                'title': 'Desenvolvimento Web com Python e Django',
                'description': 'Aprenda a construir aplicações web robustas e escaláveis usando o Django. Do padrão MVT à criação de modelos, visualizações, rotas e formulários seguros.',
                'materials': [
                    {
                        'title': 'Views e Roteamento de URLs',
                        'description': 'Como estruturar requisições, views baseadas em função, decorators e mapeamento de rotas.',
                        'url': 'course_materials/2_views_e_urls.pdf',
                    },
                    {
                        'title': 'Templates e Formulários no Django',
                        'description': 'Herança de templates com Jinja/Django tags, formulários e validação de dados.',
                        'url': 'course_materials/2_templates_e_formularios.pdf',
                    },
                    {
                        'title': 'Modelos e Banco de Dados com ORM',
                        'description': 'Criação de migrations, relacionamentos ForeignKey e consultas otimizadas.',
                        'url': 'course_materials/2_modelos_e_banco_de_dados.pdf',
                    },
                ],
            },
            {
                'teacher_username': 'prof.carlos',
                'title': 'Finanças Pessoais e Planejamento de Metas',
                'description': 'Educação financeira essencial para o dia a dia. Aprenda a montar seu orçamento, construir uma reserva de emergência sólida e investir para atingir seus objetivos.',
                'materials': [
                    {
                        'title': 'Orçamento Mensal Inteligente',
                        'description': 'Técnicas de categorização de receitas, controle de despesas e redução de desperdícios.',
                        'url': 'course_materials/3_orcamento_mensal.pdf',
                    },
                    {
                        'title': 'Construção da Reserva de Emergência',
                        'description': 'Onde alocar fundos emergenciais com liquidez diária e baixo risco.',
                        'url': 'course_materials/3_reserva_de_emergencia.pdf',
                    },
                    {
                        'title': 'Planejamento e Conquista de Metas',
                        'description': 'Estratégias de investimento a médio e longo prazo para independência financeira.',
                        'url': 'course_materials/3_planejamento_de_metas.pdf',
                    },
                ],
            },
            {
                'teacher_username': 'prof.mariana',
                'title': 'Design de Experiência do Usuário (UX/UI)',
                'description': 'Metodologias práticas de Design Thinking e User Centered Design. Desde a pesquisa com usuários reais até a arquitetura da informação e criação de protótipos.',
                'materials': [
                    {
                        'title': 'Pesquisa com Usuários e Personas',
                        'description': 'Entrevistas qualitativas, questionários, mapeamento de jornadas e definição de personas.',
                        'url': 'course_materials/4_pesquisa_com_usuarios.pdf',
                    },
                    {
                        'title': 'Arquitetura da Informação e Wireframes',
                        'description': 'Organização de fluxos de navegação, taxonomia e wireframes de baixa fidelidade.',
                        'url': 'course_materials/4_arquitetura_da_informacao.pdf',
                    },
                    {
                        'title': 'Prototipação Interativa e Testes de Usabilidade',
                        'description': 'Prototipação navegável, testes com usuários e iteração com base em métricas.',
                        'url': 'course_materials/4_prototipacao_e_testes.pdf',
                    },
                ],
            },
            {
                'teacher_username': 'prof.roberto',
                'title': 'Sustentabilidade e Gestão de Recursos Naturais',
                'description': 'Fundamentos de responsabilidade socioambiental, preservação de ecossistemas, economia circular e implementação de projetos ecológicos em comunidades e empresas.',
                'materials': [
                    {
                        'title': 'Consumo Consciente e Economia Circular',
                        'description': 'Redução de pegada de carbono, descarte correto de resíduos e modelos circulares.',
                        'url': 'course_materials/5_consumo_consciente.pdf',
                    },
                    {
                        'title': 'Gestão de Recursos Naturais',
                        'description': 'Preservação da água, transição energética e manejo florestal sustentável.',
                        'url': 'course_materials/5_recursos_naturais.pdf',
                    },
                    {
                        'title': 'Projetos Sustentáveis Comunitários',
                        'description': 'Como estruturar iniciativas com impacto social positivo e viabilidade econômica.',
                        'url': 'course_materials/5_projetos_sustentaveis.pdf',
                    },
                ],
            },
            {
                'teacher_username': 'grossi',
                'title': 'Análise e Estruturas de Algoritmos',
                'description': 'Estudo aprofundado sobre eficiência de algoritmos computacionais, notação Big-O, busca, ordenação e estruturas de dados dinâmicas.',
                'materials': [
                    {
                        'title': 'Introdução à Análise de Algoritmos',
                        'description': 'Notação assintótica (O, Ômega, Theta) e análise do pior e melhor caso.',
                        'url': 'course_materials/FPAA_Aula_01_-_Introdução_a_Analise_de_Algoritmos.pdf',
                    },
                    {
                        'title': 'Cronograma e Diretrizes da Disciplina',
                        'description': 'Plano de aulas, critérios de avaliação e bibliografia recomendada.',
                        'url': 'course_materials/cronograma_DAD_2026_1.pdf',
                    },
                    {
                        'title': 'Aula Prática em Vídeo',
                        'description': 'Gravação explicativa sobre resolução e implementação de algoritmos.',
                        'url': 'course_materials/video_1.mp4',
                    },
                ],
            },
        ]

        created_courses = []
        for c_data in courses_data:
            teacher = teachers[c_data['teacher_username']]
            course, _ = Course.objects.get_or_create(
                teacher=teacher,
                title=c_data['title'],
                defaults={'description': c_data['description']},
            )
            created_courses.append(course)
            self.stdout.write(self.style.SUCCESS(f"Curso garantido: {course.title} (Prof: {teacher.get_full_name()})"))

            for mat_data in c_data['materials']:
                material, mat_created = CourseMaterial.objects.get_or_create(
                    course=course,
                    title=mat_data['title'],
                    defaults={
                        'description': mat_data['description'],
                        'url': mat_data['url'],
                    },
                )
                if mat_created:
                    self.stdout.write(f"  - Material adicionado: {material.title}")

        # 4. Inscrições, Conclusões e Certificados
        enrollments_plan = [
            # Lucas concluiu IA completamente
            {
                'student_username': 'aluno.lucas',
                'course_title': 'Inteligência Artificial e Machine Learning',
                'completed_all': True,
            },
            # Lucas está fazendo Django (concluiu 2 materiais)
            {
                'student_username': 'aluno.lucas',
                'course_title': 'Desenvolvimento Web com Python e Django',
                'completed_count': 2,
            },
            # Beatriz concluiu Django completamente
            {
                'student_username': 'aluna.beatriz',
                'course_title': 'Desenvolvimento Web com Python e Django',
                'completed_all': True,
            },
            # Beatriz está fazendo UX/UI (concluiu 1 material)
            {
                'student_username': 'aluna.beatriz',
                'course_title': 'Design de Experiência do Usuário (UX/UI)',
                'completed_count': 1,
            },
            # Gabriel concluiu Finanças completamente
            {
                'student_username': 'aluno.gabriel',
                'course_title': 'Finanças Pessoais e Planejamento de Metas',
                'completed_all': True,
            },
            # Gabriel está inscrito em Sustentabilidade
            {
                'student_username': 'aluno.gabriel',
                'course_title': 'Sustentabilidade e Gestão de Recursos Naturais',
                'completed_count': 1,
            },
            # Camila está inscrita em Algoritmos e UX
            {
                'student_username': 'aluna.camila',
                'course_title': 'Análise e Estruturas de Algoritmos',
                'completed_count': 2,
            },
            {
                'student_username': 'aluna.camila',
                'course_title': 'Design de Experiência do Usuário (UX/UI)',
                'completed_all': True,
            },
            # Pedro está inscrito em Finanças e Django
            {
                'student_username': 'aluno.pedro',
                'course_title': 'Finanças Pessoais e Planejamento de Metas',
                'completed_count': 1,
            },
            {
                'student_username': 'aluno.pedro',
                'course_title': 'Desenvolvimento Web com Python e Django',
                'completed_count': 0,
            },
        ]

        for plan in enrollments_plan:
            student = students[plan['student_username']]
            course = Course.objects.get(title=plan['course_title'])

            enrollment, _ = CourseEnrollment.objects.get_or_create(
                student=student,
                course=course,
            )

            materials = list(course.materials.all())
            if plan.get('completed_all'):
                to_complete = materials
            else:
                count = plan.get('completed_count', 0)
                to_complete = materials[:count]

            for mat in to_complete:
                CompletedMaterial.objects.get_or_create(
                    enrollment=enrollment,
                    material=mat,
                )

            if plan.get('completed_all') and materials:
                Certificate.objects.get_or_create(
                    student=student,
                    course=course,
                )
                self.stdout.write(f"  -> Certificado gerado para {student.username} em '{course.title}'")

        self.stdout.write(self.style.SUCCESS('\nPopulação do banco de dados concluída com sucesso!'))
        self.stdout.write(f"Todos os usuários foram criados com a senha padrão: '{default_password}'")
