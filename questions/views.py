from django.http import Http404
from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

QUESTIONS = [
    {
        'id': 1,
        'title': 'How to build a moon park?',
        'text': 'Guys, I have trouble with a moon park.',
        'rating': 5,
        'rating_state': 'neutral',
        'tags': ['black-jack', 'bender'],
        'answers_count': 2,
        'time': '3 mins ago',
    },
    {
        'id': 2,
        'title': 'How does Django work?',
        'text': 'I want to understand Django templates.',
        'rating': 8,
        'rating_state': 'liked',
        'tags': ['django', 'python'],
        'answers_count': 1,
        'time': '10 mins ago',
    },
    {
        'id': 3,
        'title': 'What is HTTP?',
        'text': 'What happens when a browser opens a website?',
        'rating': 2,
        'rating_state': 'disliked',
        'tags': ['python', 'web'],
        'answers_count': 1,
        'time': '20 mins ago',
    },
]
ANSWERS = [
    {
        'id': 1,
        'question_id': 1,
        'text': 'You can start by creating a simple plan.',
        'rating': 5,
        'rating_state': 'neutral',
        'is_correct': True,
        'time': '2 mins ago',
    },
    {
        'id': 2,
        'question_id': 1,
        'text': 'I think you should ask Bender for help.',
        'rating': 3,
        'rating_state': 'liked',
        'is_correct': False,
        'time': '1 min ago',
    },
    {
        'id': 3,
        'question_id': 2,
        'text': 'Django is a Python web framework.',
        'rating': 7,
        'rating_state': 'neutral',
        'is_correct': True,
        'time': '5 mins ago',
    },
    {
        'id': 4,
        'question_id': 3,
        'text': 'HTTP defines requests and responses.',
        'rating': 4,
        'rating_state': 'neutral',
        'is_correct': False,
        'time': '10 mins ago',
    },
]

def paginate(objects_list, request, per_page = 10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)

    try: 
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return page


def index(request):
    page = paginate(QUESTIONS, request, per_page=2)
    return render(request, 'questions/index.html', {'questions': page.object_list, 'page_obj': page})


def hot(request):
    hot_questions = sorted (
        QUESTIONS, 
        key = lambda question: question['rating'],
        reverse = True
        )
    page = paginate(hot_questions, request, per_page=2)
    return render(
        request, 
        'questions/hot.html',
        {
            'questions': page.object_list,
            'page_obj': page
        }
    )


def tag(request, tag_name):
    filtered_questions = []

    for item in QUESTIONS:
        if tag_name in item['tags']:
            filtered_questions.append(item)

    page = paginate(filtered_questions, request, per_page=2)

    return render(
        request,
        'questions/tag.html',
        {
            'questions': page.object_list,
            'page_obj': page,
            'tag_name': tag_name
        }
    )


def question(request, question_id): 
    for item in QUESTIONS:
        if item['id'] == question_id:
            answers = []
            for answer in ANSWERS:
                if answer['question_id'] == question_id:
                    answers.append(answer)
            page = paginate(answers, request, per_page=1)
            return render(request, 'questions/question.html', {'question':item, 'answers': page.object_list, 'page_obj': page})
    raise Http404("Вопрос не найден")


def ask(request):
    return render(request, 'questions/ask.html')