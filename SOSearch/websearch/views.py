from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from haystack.views import SearchView
from .models import *

# Create your views here.
def index(request):
    sort_by = request.GET.get('sort_by', 'viewed')
    question_list = Question.objects.order_by('-' + sort_by)
    paginator = Paginator(question_list, 10)
    page = request.GET.get('page')
    try:
        question_list = paginator.page(page)
    except PageNotAnInteger:
        question_list = paginator.page(1)
    except EmptyPage:
        question_list = paginator.page(paginator.num_pages)
    finally:
        for question in question_list:
            answers = Answer.objects.filter(rid=question.id)
            accepted = False
            for answer in answers:
                if answer.accepted == 1:
                    accepted = True
                    break
            question.accepted = accepted
            question.answer_num = len(answers)
            question.tag_list = question.tags.split(',')
            try:
                question.asked_user = User.objects.filter(rid=question.id).exclude(action='edited').get()
            except Exception as e:
                pass
    context = {
        'question_list': question_list,
        'sort_by': sort_by
    }
    return render(request, 'websearch/index.html', context)

def detail(request, question_id):
    sort_by = request.GET.get('sort_by', 'vote')
    question = get_object_or_404(Question, pk=question_id)
    question.tag_list = question.tags.split(',')
    question.users = User.objects.filter(rid=question.id)
    question.comments = Comment.objects.filter(rid=question.id)
    question.answers = Answer.objects.filter(rid=question.id)
    question.linked_questions = LinkedQuestion.objects.filter(rid=question.id)
    question.related_questions = RelatedQuestion.objects.filter(rid=question.id)
    for answer in question.answers:
        answer.users = User.objects.filter(rid=answer.id)
        answer.comments = Comment.objects.filter(rid=answer.id)
        try:
            answer.time = answer.users.filter(action='answered').get().time
        except Exception as e:
            answer.time = '1970-01-01 00:00:00Z'
    if sort_by == 'comments':
        question.answers = sorted(question.answers, key=lambda o: len(o.comments), reverse=True)
    elif sort_by == 'time':
        question.answers = sorted(question.answers, key=lambda o: o.time, reverse=True)
    context = {
        'question': question,
        'sort_by': sort_by
    }
    return render(request, 'websearch/detail.html', context)


class MySeachView(SearchView):

    def __init__(self):
        super(MySeachView, self).__init__()
        self.results_per_page = 10

    def get_context(self):
        sort_by = self.request.GET.get('sort_by', '')
        if sort_by:
            self.results = self.results.order_by('-' + sort_by)
        (paginator, page) = self.build_page()

        context = {
            'query': self.query,
            'form': self.form,
            'page': page,
            'paginator': paginator,
            'suggestion': None,
            'sort_by': sort_by,
        }

        if hasattr(self.results, 'query') and self.results.query.backend.include_spelling:
            context['suggestion'] = self.form.get_suggestion()

        for result in page.object_list:
            if result.model_name == 'question':
                question = result.object
                answers = Answer.objects.filter(rid=question.id)
                accepted = False
                for answer in answers:
                    if answer.accepted == 1:
                        accepted = True
                        break
                question.accepted = accepted
                question.answer_num = len(answers)
                question.tag_list = question.tags.split(',')
                try:
                    question.asked_user = User.objects.filter(rid=question.id).exclude(action='edited').get()
                except Exception as e:
                    pass
            elif result.model_name == 'answer':
                answer = result.object
                answer.title = Question.objects.filter(id=answer.rid).get().title
                try:
                    answer.answered_user = User.objects.filter(rid=answer.id).exclude(action='edited')[0]
                except Exception as e:
                    pass

        context.update(self.extra_context())

        return context
