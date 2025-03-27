from django.contrib.auth.decorators import login_required
from .models import Question, Option, Vote, Poll, Comment, Gallery, Image
import os
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from apps.societies.models import Society
from .forms import *


def panels(request):
    return render(request, 'panels.html')

@login_required
def create_poll(request, society_id):
    society = get_object_or_404(Society, id=society_id)

    if request.method == 'POST':
        form = PollForm(request.POST)
        if form.is_valid():
            poll = form.save(commit=False)
            poll.society = society
            poll.save()
            return redirect('panels:add_question', society_id=society.id, poll_id=poll.id)
    else:
        form = PollForm()

    return render(request, 'create_poll.html', {'form': form, 'society': society})

@login_required
def add_question(request, society_id, poll_id):
    society = get_object_or_404(Society, id=society_id)
    poll = get_object_or_404(Poll, id=poll_id, society=society)

    extra_forms = int(request.GET.get('extra', 3))  # default to 3 options

    OptionFormSetCustom = modelformset_factory(
        Option,
        fields=('option_text',),
        extra=extra_forms,
        can_delete=False
    )

    if request.method == 'POST':
        q_form = QuestionForm(request.POST)
        o_formset = OptionFormSetCustom(request.POST)

        if q_form.is_valid() and o_formset.is_valid():
            question = q_form.save(commit=False)
            question.poll = poll
            question.save()

            for form in o_formset:
                option = form.save(commit=False)
                option.question = question
                option.save()

            return redirect('panels:poll_list', society_id=society.id)
    else:
        q_form = QuestionForm()
        o_formset = OptionFormSetCustom(queryset=Option.objects.none())

    return render(request, 'add_question.html', {
        'poll': poll,
        'society': society,
        'q_form': q_form,
        'o_formset': o_formset,
        'extra_forms': extra_forms,
    })


@login_required
def poll_list(request, society_id):
    society = get_object_or_404(Society, id=society_id)
    polls = Poll.objects.filter(society=society)
    return render(request, 'poll_list.html', {'polls': polls, 'society': society})


@login_required
def vote(request, society_id, poll_id, question_id):
    society = get_object_or_404(Society, id=society_id)
    poll = get_object_or_404(Poll, id=poll_id, society=society)
    question = get_object_or_404(Question, id=question_id, poll=poll)

    if poll.is_closed():
        return render(request, 'poll_closed.html', {'poll': poll})

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
            return redirect('panels:poll_result', society_id=society.id, poll_id=poll.id, question_id=question.id)

    return render(request, 'vote.html', {
        'society': society,
        'poll': poll,
        'question': question,
        'options': options,
        'user_selected_option': user_selected_option
    })

@login_required
def poll_result(request, society_id, poll_id, question_id):
    society = get_object_or_404(Society, id=society_id)
    poll = get_object_or_404(Poll, id=poll_id, society=society)
    question = get_object_or_404(Question, id=question_id, poll=poll)
    options = question.options.all()
    total_votes = sum([opt.option_count for opt in options])

    return render(request, 'poll_result.html', {
        'society': society,
        'poll': poll,
        'question': question,
        'options': options,
        'total_votes': total_votes
    })

@login_required
def cancel_vote(request, society_id, poll_id, question_id):
    society = get_object_or_404(Society, id=society_id)
    poll = get_object_or_404(Poll, id=poll_id, society=society)
    question = get_object_or_404(Question, id=question_id, poll=poll)

    vote = Vote.objects.filter(voted_by=request.user, option__question=question).first()

    if vote:
        selected_option = vote.option
        vote.delete()
        selected_option.option_count = max(selected_option.option_count - 1, 0)
        selected_option.save()

    return redirect('panels:vote', society_id=society.id, poll_id=poll.id, question_id=question.id)


#gallery
@login_required
def society_gallery_list(request, society_id):
    society = get_object_or_404(Society, id=society_id)
    galleries = Gallery.objects.filter(society=society)
    return render(request, 'society_gallery_list.html', {
        'society': society,
        'galleries': galleries,
    })


@login_required
def create_gallery(request, society_id):
    society = get_object_or_404(Society, id=society_id)

    if request.method == 'POST':
        form = GalleryForm(request.POST)
        if form.is_valid():
            gallery = form.save(commit=False)
            gallery.society = society
            gallery.save()
            return redirect('panels:gallery_detail', society_id=society.id, gallery_id=gallery.id)
    else:
        form = GalleryForm()

    return render(request, 'create_gallery.html', {'form': form, 'society': society})


@login_required
def gallery_detail(request, society_id, gallery_id):
    society = get_object_or_404(Society, id=society_id)
    gallery = get_object_or_404(Gallery, id=gallery_id, society=society)
    images = gallery.images.all()
    return render(request, 'gallery_detail.html', {
        'society': society,
        'gallery': gallery,
        'images': images
    })


@login_required
def upload_image(request, society_id, gallery_id):
    society = get_object_or_404(Society, id=society_id)
    gallery = get_object_or_404(Gallery, id=gallery_id, society=society)

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.gallery = gallery
            image.uploaded_by = request.user
            image.save()
            return redirect('panels:gallery_detail', society_id=society.id, gallery_id=gallery.id)
    else:
        form = ImageUploadForm()

    return render(request, 'upload_image.html', {
        'form': form,
        'gallery': gallery,
        'society': society
    })


@login_required
def delete_image(request, society_id, image_id):
    society = get_object_or_404(Society, id=society_id)
    image = get_object_or_404(Image, id=image_id)
    gallery = image.gallery

    if gallery.society.id != society.id:
        return HttpResponseForbidden("You can't delete this image.")

    if request.method == 'POST':
        image.delete()
        return redirect('panels:gallery_detail', society_id=society.id, gallery_id=gallery.id)

    return render(request, 'confirm_delete.html', {
        'image': image,
        'society': society
    })

#comment
@login_required
def society_comment_feed(request, society_id):
    society = get_object_or_404(Society, id=society_id)
    comments = society.comments.all().order_by('-created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.society = society
            comment.author = request.user
            comment.save()
            return redirect('panels:society_comment_feed', society_id=society.id)
    else:
        form = CommentForm()

    return render(request, 'society_comment_feed.html', {
        'society': society,
        'comments': comments,
        'form': form
    })

@login_required
def edit_comment(request, society_id, comment_id):
    society = get_object_or_404(Society, id=society_id)
    comment = get_object_or_404(Comment, id=comment_id, society=society)

    if comment.author != request.user:
        messages.error(request, "You don't have permission to edit this comment.")
        return redirect('panels:society_comment_feed', society_id=society.id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('panels:society_comment_feed', society_id=society.id)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'edit_comment.html', {
        'form': form,
        'comment': comment,
        'society': society,
    })


@login_required
def delete_comment(request, society_id, comment_id):
    society = get_object_or_404(Society, id=society_id)
    comment = get_object_or_404(Comment, id=comment_id, society=society)

    if comment.author != request.user:
        messages.error(request, "You don't have permission to delete this comment.")
        return redirect('panels:society_comment_feed', society_id=society.id)

    if request.method == 'POST':
        comment.delete()
        return redirect('panels:society_comment_feed', society_id=society.id)

    return render(request, 'confirm_delete_comment.html', {
        'comment': comment,
        'society': society
    })


@login_required
def toggle_like_comment(request, society_id, comment_id):
    society = get_object_or_404(Society, id=society_id)
    comment = get_object_or_404(Comment, id=comment_id, society=society)

    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)

    return redirect('panels:society_comment_feed', society_id=society.id)
