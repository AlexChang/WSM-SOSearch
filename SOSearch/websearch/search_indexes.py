import datetime
from haystack import indexes
from .models import Question, Answer


class QuestionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    vote = indexes.IntegerField(model_attr='vote')
    # author = indexes.CharField(model_attr='user')
    # pub_date = indexes.DateTimeField(model_attr='pub_date')

    def get_model(self):
        return Question

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
        # return self.get_model().objects.filter(pub_date__lte=datetime.datetime.now())


class AnswerIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    vote = indexes.IntegerField(model_attr='vote')
    # author = indexes.CharField(model_attr='user')
    # pub_date = indexes.DateTimeField(model_attr='pub_date')

    def get_model(self):
        return Answer

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
        # return self.get_model().objects.filter(pub_date__lte=datetime.datetime.now())