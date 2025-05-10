# views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Article, Profile, Subjects, StudentGroupMembership, Grades, Events
from .forms import ProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def home_page(request):
    articles = Article.objects.all()
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'main/home.html', {
        'articles': articles,
        'profile': profile,
        'form': form,
    })


def article_detail(request, article_id):
    article = Article.objects.get(id=article_id)
    return render(request, 'main/article_detail.html', {'article': article})


@login_required
def dashboard(request):
    profile = request.user.profile
    return render(request, 'main/dashboard.html', {'profile': profile})


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


def study(request):
    return render(request, 'curricular/study.html')


@login_required
def events(request):
    # Получаем все мероприятия, где доступность True
    events_list = Events.objects.filter(available=True)

    return render(request, 'extracurricular/events.html', {
        'events': events_list
    })


def registrations(request):
    return render(request, 'extracurricular/registrations.html')


def shop(request):
    return render(request, 'shop/shop.html')


def orders(request):
    return render(request, 'shop/orders.html')


def operations(request):
    return render(request, 'main/operations.html')