from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Question, Answer, Tag


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
    return render(request, "questions/index.html", {
        "questions": page.object_list, "page_obj": page
    })


def hot(request):
    page = paginate(Question.objects.best(), request, per_page=2)
    return render(request, "questions/hot.html", {
        "questions": page.object_list, "page_obj": page
    })


def tag(request, tag_name):
    current_tag = get_object_or_404(Tag, slug=tag_name)
    page = paginate(Question.objects.by_tag(current_tag.slug), request, per_page=2)
    return render(request, "questions/tag.html", {
        "questions": page.object_list,
        "page_obj": page, "tag_name": current_tag.name
    })


def question(request, question_id):
    current_question = get_object_or_404(
        Question.objects.with_stats(), pk=question_id
    )
    page = paginate(Answer.objects.for_question(question_id), request, per_page=10)
    return render(request, "questions/question.html", {
        "question": current_question,
        "answers": page.object_list, "page_obj": page
    })



def ask(request):
    return render(request, 'questions/ask.html')