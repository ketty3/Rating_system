
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth import logout
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from .models import  Profile
from .forms import ProfileForm
from .models import Article
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
#def home_page(request):
    #articles = Article.objects.all()
    #return render(request, 'main/home.html', {'articles': articles})
def article_detail(request, article_id):
    article = Article.objects.get(id=article_id)
    return render(request, 'main/article_detail.html', {'article': article})
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def dashboard(request):
    profile = request.user.profile
    context = {
        'profile': profile,
        #'academic_trend': 'up' if profile.academic_change >= 0 else 'down',
        #'activity_trend': 'up' if profile.activity_change >= 0 else 'down',
    }
    return render(request, 'main/dashboard.html', context)
from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('home')  # перезагрузка страницы
    else:
        form = ProfileForm(instance=profile)

    context = {
        'profile': profile,
        'form': form,
    }

    return render(request, 'main/profile.html', context)


def news(request):
    return render(request, 'main/news.html')
def study(request):
    return render(request, 'curricular/study.html')
def subjects(request):
    return render(request, 'curricular/subjects.html')
def events(request):
    return render(request, 'extracurricular/events.html')
def registrations(request):
    return render(request, 'extracurricular/registrations.html')
def shop(request):
    return render(request, 'shop/shop.html')
def orders(request):
    return render(request, 'shop/orders.html')
def operations(request):
    return render(request, 'main/operations.html')




