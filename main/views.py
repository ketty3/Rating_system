# views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Article, Profile, Subjects, StudentGroupMembership, Grades, Events, EventRoles, Registrations, \
    MoneyOperations
from .forms import ProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages


@login_required
def home_page(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль успешно обновлён")
            return redirect('home')
        else:
            print("Ошибки формы:", form.errors)
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'main/home.html', {
        'profile': profile,
        'form': form,
    })




def article_detail(request, article_id):
    article = Article.objects.get(id=article_id)
    return render(request, 'main/article_detail.html', {'article': article})

@login_required
def dashboard(request):
    profile = request.user.profile

    # Получаем средний балл по учебе
    avg_grade_user = get_student_avg_grade(request.user)

    # Получаем внеучебные баллы
    extra_points_user = get_extra_points(request.user)

    # Получаем топ по оценкам
    top_students_grades = (
        Grades.objects.values('student_id')
        .annotate(avg_grade=Avg('grade'))
        .order_by('-avg_grade')[:10]
    )

    students_top_grades = []
    for item in top_students_grades:
        user = User.objects.get(id=item['student_id'])
        student_profile = Profile.objects.get(user=user)
        students_top_grades.append({
            'full_name': student_profile.get_full_name,
            'avg_grade': round(item['avg_grade'], 2) if item['avg_grade'] else 0.0,
        })

    # Определяем место пользователя по оценкам
    all_grades = (
        Grades.objects.values('student_id')
        .annotate(avg_grade=Avg('grade'))
        .order_by('-avg_grade')
    )

    user_rank_grades = None
    for idx, entry in enumerate(all_grades, start=1):
        if entry['student_id'] == request.user.id:
            user_rank_grades = idx
            break

    # Получаем топ по внеклассным баллам
    top_students_extra = (
        MoneyOperations.objects.values('user')
        .annotate(extra_points=Sum('quantity'))
        .filter(extra_points__gt=0)
        .order_by('-extra_points')[:10]
    )

    students_top_extra = []
    for item in top_students_extra:
        try:
            user = User.objects.get(id=item['user'])
            student_profile = Profile.objects.get(user=user)
            students_top_extra.append({
                'full_name': student_profile.get_full_name,
                'extra_points': round(float(item['extra_points']), 2)
            })
        except User.DoesNotExist:
            continue

    # Определяем место пользователя во внеклассном рейтинге
    all_extra_points = (
        MoneyOperations.objects.values('user')
        .annotate(extra_points=Sum('quantity'))
        .filter(extra_points__gt=0)
        .order_by('-extra_points')
    )

    user_extra_rank = None
    for idx, entry in enumerate(all_extra_points, start=1):
        if entry['user'] == request.user.id:
            user_extra_rank = idx
            break

    context = {
        'profile': profile,
        'avg_grade_user': avg_grade_user,
        'extra_points_user': extra_points_user,
        'students_top_grades': students_top_grades,
        'students_top_extra': students_top_extra,
        'user_rank_grades': user_rank_grades,  # Теперь эта переменная определена
        'user_extra_rank': user_extra_rank or '-',
    }

    return render(request, 'main/dashboard.html', context)


@login_required
def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлён.')
            return redirect('profile_view')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'main/home.html', {
        'profile': profile,
        'form': form,
        'articles': Article.objects.all()
    })


@login_required
def subjects_taught(request):
    # Получаем все предметы, где текущий пользователь — преподаватель
    subjects = Subjects.objects.filter(teacher_id=request.user).select_related('group_id').order_by('semestr_id')

    semesters = {}

    for subject in subjects:
        semester_number = subject.semestr_id
        if semester_number not in semesters:
            semesters[semester_number] = []

        memberships = StudentGroupMembership.objects.filter(group=subject.group_id)
        students_with_grades = []

        for membership in memberships:
            grade_obj, created = Grades.objects.get_or_create(
                student_id=membership.user,
                subject_id=subject,
                defaults={'grade': None}
            )

            students_with_grades.append({
                'student': membership.user,
                'grade': grade_obj.grade,
                'grades_id': grade_obj.grades_id,  # <<< Здесь используется реальное имя поля
                'student_id': membership.user.id,
            })

        semesters[semester_number].append({
            'subject': subject,
            'students_with_grades': students_with_grades,
        })

    return render(request, 'curricular/subjects.html', {
        'semesters': semesters
    })

@login_required
def save_grades(request, subject_id):
    subject = get_object_or_404(Subjects, id=subject_id, teacher_id=request.user)

    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('grade_'):
                student_id = int(key.split('_')[1])
                try:
                    grade_float = float(value) if value.strip() else None
                except ValueError:
                    continue

                Grades.objects.update_or_create(
                    student_id_id=student_id,
                    subject_id=subject,
                    defaults={'grade': grade_float}
                )

        messages.success(request, 'Оценки сохранены')
        return redirect('subjects_taught')


def news(request):
    return render(request, 'main/news.html')


@login_required
def study(request):
    profile = request.user.profile

    # Только для студентов
    if profile.role != 'ST':
        return render(request, 'curricular/study.html', {
            'error': "Доступ только для студентов"
        })

    # Получаем все оценки студента
    grades = Grades.objects.filter(student_id=request.user).select_related('subject_id')

    # Подготовка данных
    subjects_with_grades = []
    for grade in grades:
        subjects_with_grades.append({
            'subject_name': grade.subject_id.subject_name,
            'grade': grade.grade,
            'subject_type': grade.subject_id.subject_type,
            'teacher': grade.subject_id.teacher_id.get_full_name(),
        })

    return render(request, 'curricular/study.html', {
        'subjects_with_grades': subjects_with_grades
    })


from .models import Events, Registrations
from .forms import EventForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def events(request):
    profile = request.user.profile
    all_events = Events.objects.all()

    # Переменные для формы создания
    form_create = EventForm(prefix='create')
    form_edit = None
    event_to_edit = None

    # Только для TE и MA показываем форму создания
    if profile.role in ['TE', 'MA']:
        if request.method == 'POST':
            if 'create_event' in request.POST:
                form_create = EventForm(request.POST, request.FILES, prefix='create')
                if form_create.is_valid():
                    form_create.save()
                    messages.success(request, 'Мероприятие создано!')
                    return redirect('events')

            elif 'edit_event' in request.POST:
                event_id = request.POST.get('event_id')
                event_to_edit = get_object_or_404(Events, event_id=event_id)
                form_edit = EventForm(request.POST, request.FILES, instance=event_to_edit, prefix='edit')

                if form_edit.is_valid():
                    form_edit.save()
                    messages.success(request, 'Мероприятие обновлено!')
                    return redirect('events')

        # Если GET и роль TE/MA — просто передаём пустую форму
        else:
            form_create = EventForm(prefix='create')

    # Для шаблона: добавляем is_registered
    for event in all_events:
        event.is_registered = event.registrations.filter(user=request.user).exists()

    return render(request, 'extracurricular/events.html', {
        'events': all_events,
        'profile': profile,
        'form_create': form_create,
        'form_edit': form_edit,
        'event_to_edit': event_to_edit,
    })

# views.py

from .models import Registrations, EventRoles

from .forms import ProfileForm, RegistrationForm
from django.forms import modelformset_factory
from django.contrib import messages


# Формсет для редактирования регистраций
@login_required
def registrations(request):
    profile = request.user.profile

    if profile.role not in ['TE', 'MA', 'AD']:
        return render(request, 'extracurricular/registrations.html', {
            'error': "Доступ запрещён"
        })

    # Получаем все регистрации
    registrations_list = Registrations.objects.select_related('user', 'event', 'e_role_id').all()

    # Создаём формсет
    RegistrationFormSet = modelformset_factory(
        Registrations,
        form=RegistrationForm,
        extra=0
    )

    if request.method == 'POST':
        formset = RegistrationFormSet(request.POST, queryset=registrations_list)

        if formset.is_valid():
            formset.save()
            messages.success(request, "Изменения успешно сохранены")
            return redirect('registrations')
    else:
        formset = RegistrationFormSet(queryset=registrations_list)

    return render(request, 'extracurricular/registrations.html', {
        'formset': formset
    })
@login_required
def register_event(request, event_id):
    profile = request.user.profile

    # Проверяем, что пользователь — студент
    if profile.role != 'ST':
        messages.error(request, "Регистрация доступна только студентам.")
        return redirect('events')

    # Получаем мероприятие
    event = get_object_or_404(Events, event_id=event_id)

    # Проверяем, зарегистрирован ли уже пользователь
    already_registered = Registrations.objects.filter(user=request.user, event=event).exists()

    if already_registered:
        messages.warning(request, "Вы уже зарегистрированы на это мероприятие.")
        return redirect('events')

    # Получаем роль "Участник" по названию
    role_participant = EventRoles.objects.filter(e_role_name='Участник').first()

    if not role_participant:
        # Если роли "Участник" нет — создаём её
        role_participant, created = EventRoles.objects.get_or_create(
            e_role_name='Участник',
            defaults={'points': 0}
        )

    # Создаём регистрацию
    Registrations.objects.create(
        event=event,
        user=request.user,
        e_role_id=role_participant,
        attendance=False,
        available=True
    )

    messages.success(request, "Вы успешно зарегистрировались на мероприятие!")
    return redirect('events')


def shop(request):
    return render(request, 'shop/shop.html')


def orders(request):
    return render(request, 'shop/orders.html')


def operations(request):
    return render(request, 'main/operations.html')

from django.db.models import Avg

def get_student_avg_grade(user):
    return Grades.objects.filter(student_id=user).aggregate(avg_grade=Avg('grade'))['avg_grade']

# views.py
from django.db.models import Sum, Q
from datetime import timedelta
import datetime

def get_extra_points(user):
    # Подсчитываем сумму всех "баллов" за последние 30 дней
    total_points = MoneyOperations.objects.filter(
        user=user,
        transaction_date__gte=datetime.date.today() - timedelta(days=30),
        quantity__gt=0
    ).aggregate(total=Sum('quantity'))['total']

    return total_points or 0