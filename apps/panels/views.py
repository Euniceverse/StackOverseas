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
            form.save(user=request.user) 
            return redirect('panels:index') 
    else:
        form = PollForm()  

    return render(request, 'create_poll.html', {'form': form})

@login_required
def index(request):
    questions = Question.objects.all()
    return render(request, 'index.html', {'questions': questions})

@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    options = question.options.all()

    user_vote = Vote.objects.filter(voted_by=request.user, option__question=question).first()
    user_selected_option = user_vote.option if user_vote else None

    if request.method == 'POST' and not user_vote:
        selected_option_id = request.POST.get('option')
        if selected_option_id:
            selected_option = get_object_or_404(Option, id=selected_option_id, question=question)

            Vote.objects.create(option=selected_option, voted_by=request.user)
            selected_option.option_count += 1
            selected_option.save()

            return redirect('panels:vote', question_id=question.id)

    return render(request, 'vote.html', {
        'question': question,
        'options': options,
        'user_selected_option': user_selected_option 
    })

from django.db import transaction

@login_required
def cancel_vote(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    vote = Vote.objects.filter(voted_by=request.user, option__question=question).first()

    if vote:
        selected_option = vote.option  
        with transaction.atomic():  
            vote.delete()  

            selected_option.refresh_from_db()
            if selected_option.option_count > 0:
                selected_option.option_count -= 1
                selected_option.save()

    return redirect('panels:vote', question_id=question.id) 
