from django.shortcuts import render, redirect
from .forms import PollForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Question, Option, Vote
from django.contrib.auth.decorators import login_required
import os

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

from .models import Gallery, Image
from .forms import GalleryForm, ImageForm

@login_required
def gallery_list(request):
    galleries = Gallery.objects.all()
    return render(request, 'gallery_list.html', {'galleries': galleries})

@login_required
def gallery_detail(request, gallery_id):
    gallery = get_object_or_404(Gallery, id=gallery_id)
    images = gallery.images.all()
    
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.gallery = gallery
            image.save()
            return redirect('panels:gallery_detail', gallery_id=gallery.id)
    else:
        form = ImageForm()

    return render(request, 'gallery_detail.html', {'gallery': gallery, 'images': images, 'form': form})

@login_required
def upload_gallery(request):
    if request.method == 'POST':
        gallery_form = GalleryForm(request.POST)
        image_form = ImageForm(request.POST, request.FILES)
        
        if gallery_form.is_valid() and image_form.is_valid():
            # 갤러리 객체를 먼저 저장하지 않음, 'commit=False'로 저장
            gallery = gallery_form.save(commit=False)
            gallery.owner = request.user  # 현재 로그인한 유저를 owner로 설정
            gallery.save()

            # 이미지 객체 저장
            image = image_form.save(commit=False)
            image.gallery = gallery  # 갤러리와 연결
            image.save()

            return redirect('panels:gallery_list')  # 업로드 완료 후 목록 페이지로 이동
    else:
        gallery_form = GalleryForm()
        image_form = ImageForm()

    return render(request, 'upload_gallery.html', {
        'gallery_form': gallery_form,
        'image_form': image_form
    })


@login_required
def delete_image(request, image_id):
    # 이미지 객체를 가져옴
    image = get_object_or_404(Image, id=image_id)

    # 이미지 소유자가 맞는지 확인
    if image.gallery.owner != request.user:
        return redirect('panels:gallery')  # 권한이 없으면 갤러리로 리디렉션

    # 파일 시스템에서 이미지 파일 삭제
    if image.image:
        image_path = image.image.path
        if os.path.exists(image_path):
            os.remove(image_path)

    # 데이터베이스에서 이미지 삭제
    image.delete()

    # 갤러리 페이지로 리디렉션
    return redirect('panels:gallery')  # 또는 'panels:gallery_detail'로 리디렉션할 수 있습니다.
