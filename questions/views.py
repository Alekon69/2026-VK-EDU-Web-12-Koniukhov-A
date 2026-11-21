from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Question, Answer, Tag, QuestionLike, AnswerLike
from .forms import QuestionForm, AnswerForm, VoteForm, CorrectAnswerForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse


def paginate(objects_list, request, per_page = 10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)

    try: 
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    page.elided_range = paginator.get_elided_page_range(
    page.number,
    on_each_side=1,
    on_ends=1
    )

    return page


def index(request):
    page = paginate(Question.objects.newest(), request, per_page=2)
    add_user_votes_to_questions(page, request.user)
    return render(request, "questions/index.html", {
        "questions": page.object_list, "page_obj": page
    })


def hot(request):
    page = paginate(Question.objects.best(), request, per_page=2)
    add_user_votes_to_questions(page, request.user)
    return render(request, "questions/hot.html", {
        "questions": page.object_list, "page_obj": page
    })


def tag(request, tag_name):
    current_tag = get_object_or_404(Tag, slug=tag_name)
    page = paginate(Question.objects.by_tag(current_tag.slug), request, per_page=2)
    add_user_votes_to_questions(page, request.user)
    return render(request, "questions/tag.html", {
        "questions": page.object_list,
        "page_obj": page, "tag_name": current_tag.name
    })



def add_user_votes_to_questions(page, user):
    questions = list(page.object_list)
    votes = {}

    if user.is_authenticated and questions:
        question_ids = [question.id for question in questions]

        votes = dict(
            QuestionLike.objects.filter(
                user=user,
                question_id__in=question_ids
            ).values_list("question_id", "value")
        )

    for question in questions:
        question.user_vote = votes.get(question.id, 0)

    page.object_list = questions



def question(request, question_id):
    current_question = get_object_or_404(
        Question.objects.with_stats(), pk=question_id
    )

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")

        answer_form = AnswerForm(request.POST)

        if answer_form.is_valid():
            
            answer = answer_form.save(
                question=current_question,
                author=request.user
            )

            answers_count = Answer.objects.filter(
                question=current_question
            ).count()

            page_number = (answers_count - 1) // 10 + 1

            url = reverse("question", args=[question_id])

            return redirect(
                f"{url}?page={page_number}#answer-{answer.id}"
            )

    else:
        answer_form = AnswerForm()

    user_vote = 0

    if request.user.is_authenticated:
        user_vote = (
            QuestionLike.objects
            .filter(
                user=request.user,
                question=current_question
            )
            .values_list("value", flat=True)
            .first() or 0
        )

    page = paginate(
        Answer.objects.for_question(question_id),
        request,
        per_page=10
    )


    answer_votes = {}

    if request.user.is_authenticated:
        answer_ids = [answer.id for answer in page.object_list]

        answer_votes = dict(
            AnswerLike.objects.filter(
                user=request.user,
                answer_id__in=answer_ids
            ).values_list("answer_id", "value")
        )

    for answer in page.object_list:
        answer.user_vote = answer_votes.get(answer.id, 0)


    return render(request, "questions/question.html", {
        "question": current_question,
        "answers": page.object_list,
        "page_obj": page,
        "answer_form": answer_form,
        "user_vote": user_vote
    })



@login_required(login_url="login")
def ask(request):
    if request.method == "POST":
        form = QuestionForm(request.POST)

        if form.is_valid():
            question = form.save(author=request.user)
            return redirect("question", question_id=question.id)
    else:
        form = QuestionForm()

    return render(request, "questions/ask.html", {
        "form": form
    })



@require_POST
def vote_question(request, question_id):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "Нужно войти в аккаунт"},
            status=403
        )
    
    form = VoteForm(request.POST)

    if not form.is_valid():
        return JsonResponse(
            {"error": form.errors["value"][0]},
            status=400
        )

    question = get_object_or_404(Question, pk=question_id)
    current_vote = form.save(request.user, question)

    rating = Question.objects.with_stats().get(
        pk=question_id
    ).rating

    return JsonResponse({
        "rating": rating,
        "user_vote": current_vote
    })



@require_POST
def vote_answer(request, answer_id):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "Нужно войти в аккаунт"},
            status=403
        )

    form = VoteForm(request.POST)

    if not form.is_valid():
        return JsonResponse(
            {"error": form.errors["value"][0]},
            status=400
        )

    answer = get_object_or_404(Answer, pk=answer_id)
    current_vote = form.save(request.user, answer)

    rating = Answer.objects.for_question(
        answer.question_id
    ).get(pk=answer_id).rating

    return JsonResponse({
        "rating": rating,
        "user_vote": current_vote
    })


@require_POST
def toggle_correct_answer(request, answer_id):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "Необходимо войти в аккаунт"},
            status=403
        )

    answer = get_object_or_404(
        Answer.objects.select_related("question"),
        pk=answer_id
    )

    form = CorrectAnswerForm(
        request.POST,
        user=request.user,
        answer=answer
    )
    
    if not form.is_valid():
        if "question_id" in form.errors:
            return JsonResponse(
                {"error": form.errors["question_id"][0]},
                status=400
            )

        return JsonResponse(
            {"error": form.non_field_errors()[0]},
            status=403
        )

    answer = form.save()

    return JsonResponse({
        "answer_id": answer.id,
        "is_correct": answer.is_correct
    })
