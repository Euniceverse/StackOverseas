from django.shortcuts import render, redirect
from .forms import PollForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Question, Option, Vote, Poll
from django.contrib.auth.decorators import login_required
import os
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Comment
from .forms import CommentForm
from apps.societies.models import Society
from .models import Gallery, Image
from .forms import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Match, MemberRating
from apps.societies.models import Society
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from apps.societies.models import Society
from .models import Match, MemberRating
from django.http import HttpResponseForbidden
from .models import HallOfFame, MemberRating
from django.utils.timezone import now



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

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils.timezone import now
from .models import Match, MemberRating, HallOfFame
from apps.societies.models import Society, Membership, MembershipRole
from django.contrib.auth import get_user_model

User = get_user_model()

def has_society_permission(user, society):
    if user.is_superuser:
        return True
    try:
        membership = Membership.objects.get(user=user, society=society)
        return membership.role in [
            MembershipRole.MANAGER,
            MembershipRole.CO_MANAGER,
            MembershipRole.EDITOR
        ]
    except Membership.DoesNotExist:
        return False

@login_required
def record_match(request, society_id):
    society = get_object_or_404(Society, id=society_id)

    if not has_society_permission(request.user, society):
        return HttpResponseForbidden("You do not have permission.")

    members = society.approved_members()
    member_ids = list(members.values_list('id', flat=True))

    if request.method == 'POST':
        player1_id = int(request.POST['player1'])
        player2_id = int(request.POST['player2'])
        winner_id = request.POST.get('winner')
        delta1 = int(request.POST.get('player1_delta', 0))
        delta2 = int(request.POST.get('player2_delta', 0))
        notes = request.POST.get('notes', '')

        if player1_id not in member_ids or player2_id not in member_ids:
            return HttpResponseForbidden("Invalid member.")

        player1 = get_object_or_404(User, id=player1_id)
        player2 = get_object_or_404(User, id=player2_id)
        winner = get_object_or_404(User, id=winner_id) if winner_id else None

        Match.objects.create(
            society=society, player1=player1, player2=player2,
            winner=winner, player1_delta=delta1, player2_delta=delta2, notes=notes
        )

        p1_rating, _ = MemberRating.objects.get_or_create(society=society, member=player1)
        p2_rating, _ = MemberRating.objects.get_or_create(society=society, member=player2)
        p1_rating.rating += delta1
        p2_rating.rating += delta2
        p1_rating.save()
        p2_rating.save()

        update_hall_of_fame(society)
        return redirect('panels:society_ranking', society_id=society.id)

    return render(request, 'record_match.html', {'society': society, 'members': members})

@login_required
def society_ranking(request, society_id):
    society = get_object_or_404(Society, id=society_id)
    rankings = MemberRating.objects.filter(society=society).order_by('-rating')
    return render(request, 'ranking.html', {'society': society, 'rankings': rankings})

@login_required
def hall_of_fame(request, society_id):
    society = get_object_or_404(Society, id=society_id)
    hof_entries = HallOfFame.objects.filter(society=society).order_by('-season')
    return render(request, 'hall_of_fame.html', {'society': society, 'hof_entries': hof_entries})

def get_current_season(mode='quarter'):
    today = now()
    year = today.year
    if mode == 'quarter':
        quarter = (today.month - 1) // 3 + 1
        return f"{year}-Q{quarter}"
    return f"{year}"

def update_hall_of_fame(society, mode='quarter'):
    season = get_current_season(mode)
    top = MemberRating.objects.filter(society=society).order_by('-rating').first()
    if top:
        HallOfFame.objects.update_or_create(
            society=society, season=season,
            defaults={'member': top.member, 'highest_rating': top.rating}
        )

@login_required
def update_hall_of_fame_view(request, society_id):
    society = get_object_or_404(Society, id=society_id)
    update_hall_of_fame(society)
    return redirect('panels:hall_of_fame', society_id=society.id)
