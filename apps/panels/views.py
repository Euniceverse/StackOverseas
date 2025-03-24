from django.shortcuts import render, redirect
from .forms import PollForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Question, Option, Vote
from django.contrib.auth.decorators import login_required

def panels(request):
    return render(request, 'panels.html')

@login_required
def create_poll(request):
    if request.method == 'POST':
        form = PollForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)  # 폼에서 저장 처리
            return redirect('panels:index')  # 성공 시 목록 페이지로 리디렉션
    else:
        form = PollForm()  # GET 요청 시 빈 폼

    return render(request, 'create_poll.html', {'form': form})

def index(request):
    questions = Question.objects.all()
    return render(request, 'index.html', {'questions': questions})

@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    if request.method == 'POST':
        selected_option_id = request.POST.get('option')
        selected_option = get_object_or_404(Option, id=selected_option_id, question=question)

        # 이미 투표한 사용자 체크
        if Vote.objects.filter(voted_by=request.user, option=selected_option).exists():
            return redirect('panels:index')  # 이미 투표한 경우 리디렉션

        # 새로운 투표 저장
        vote = Vote(option=selected_option, voted_by=request.user)
        vote.save()

        selected_option.save()

        return redirect('panels:index')

    options = question.options.all()
    return render(request, 'vote.html', {'question': question, 'options': options})
