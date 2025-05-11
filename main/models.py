from django.db import models
from django.contrib.auth.models import User
class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
# Профиль пользователя
class Profile(models.Model):
    ROLES = [
        ('ST', 'Студент'),
        ('TE', 'Преподаватель'),
        ('AD', 'Администратор'),
        ('MA', 'Менеджер'),
        ('PR', 'Продавец'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=50, verbose_name='Отчество', blank=True)
    role = models.CharField(max_length=2, choices=ROLES, verbose_name='Роль')
    group = models.ForeignKey('Groups', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Группа')
    user_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True, verbose_name='Фото профиля')

    def __str__(self):
        return f'{self.user.last_name} {self.user.first_name} {self.middle_name or ""}'

    def get_full_name(self):
        return f'{self.user.last_name} {self.user.first_name} {self.middle_name or ""}'


# Предметы
class Subjects(models.Model):
    subject_id = models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=100, verbose_name='Название предмета')
    teacher_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subjects_taught', verbose_name='Преподаватель')
    semestr_id = models.IntegerField(verbose_name='Семестр')
    group_id = models.ForeignKey('Groups', on_delete=models.CASCADE, related_name='subjects', verbose_name='Группа')
    subject_type = models.CharField(max_length=50, verbose_name='Тип предмета')

    def __str__(self):
        return self.subject_name


# Оценки
class Grades(models.Model):
    grades_id = models.AutoField(primary_key=True)
    grade = models.FloatField(verbose_name='Оценка')
    subject_id = models.ForeignKey(Subjects, on_delete=models.CASCADE, related_name='grades', verbose_name='Предмет')
    student_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_grades', verbose_name='Студент')

    def __str__(self):
        return f"{self.student_id} - {self.subject_id}: {self.grade}"


# Группы
class Groups(models.Model):
    group_id = models.AutoField(primary_key=True)
    group_name = models.CharField(max_length=50, verbose_name='Название группы')
    students = models.ManyToManyField(User, through='StudentGroupMembership', related_name='groups_joined', verbose_name='Студенты')

    def __str__(self):
        return self.group_name

class StudentGroupMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Groups, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'group')


# Мероприятия
class Events(models.Model):
    event_id = models.AutoField(primary_key=True)
    date = models.DateField(verbose_name='Дата')
    time = models.TimeField(verbose_name='Время')
    event_name = models.CharField(max_length=100, verbose_name='Название мероприятия')
    place = models.CharField(max_length=100, verbose_name='Место проведения')
    available = models.BooleanField(default=True, verbose_name='Доступность')
    notes = models.TextField(blank=True, null=True, verbose_name='Примечания')
    event_photo = models.ImageField(upload_to='event_photos/', blank=True, null=True, verbose_name='Фото мероприятия')

    def __str__(self):
        return self.event_name


# Достижения
class Achievements(models.Model):
    achieve_id = models.AutoField(primary_key=True)
    achieve_name = models.CharField(max_length=100, verbose_name='Название достижения')
    achieve_description = models.TextField(verbose_name='Описание достижения')
    condition = models.TextField(verbose_name='Условия получения')
    achieve_photo = models.ImageField(upload_to='achievement_photos/', blank=True, null=True, verbose_name='Фото достижения')
    reward_money = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Награда (денежная)')

    def __str__(self):
        return self.achieve_name


# Заказы
class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='Пользователь')
    order_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    merch = models.ForeignKey('Merch', on_delete=models.CASCADE, related_name='orders', verbose_name='Товар')
    merch_count = models.PositiveIntegerField(verbose_name='Количество товара')
    order_summa = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма заказа')

    def __str__(self):
        return f"Order #{self.order_id} by {self.user}"


# Товары
class Merch(models.Model):
    merch_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=50, verbose_name='Тип товара')
    count = models.PositiveIntegerField(verbose_name='Количество')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    merch_name = models.CharField(max_length=100, verbose_name='Название товара')
    merch_photo = models.ImageField(upload_to='merch_photos/', blank=True, null=True, verbose_name='Фото товара')

    def __str__(self):
        return self.merch_name


# Регистрации на мероприятия
class Registrations(models.Model):
    registration_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Events, on_delete=models.CASCADE, related_name='registrations', verbose_name='Мероприятие')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations', verbose_name='Пользователь')
    e_role_id = models.ForeignKey('EventRoles', on_delete=models.CASCADE, related_name='registrations', verbose_name='Роль на мероприятии')
    attendance = models.BooleanField(default=False, verbose_name='Посещение')
    available = models.BooleanField(default=True, verbose_name='Доступность')

    def __str__(self):
        return f"Registration for {self.event.event_name} by {self.user}"


# Роли на мероприятиях
class EventRoles(models.Model):
    e_role_id = models.AutoField(primary_key=True)
    e_role_name = models.CharField(max_length=50, verbose_name='Название роли')
    points = models.PositiveIntegerField(verbose_name='Баллы за роль')

    def __str__(self):
        return self.e_role_name


# Финансовые операции
class MoneyOperations(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='money_operations', verbose_name='Пользователь')
    type = models.CharField(max_length=50, verbose_name='Тип операции')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    for_what = models.CharField(max_length=100, verbose_name='За что')
    transaction_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction #{self.transaction_id} by {self.user}"
