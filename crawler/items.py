import scrapy

class Question(scrapy.Item):
    # question
    id = scrapy.Field()
    title = scrapy.Field()
    link = scrapy.Field()
    asked = scrapy.Field()
    viewed = scrapy.Field()
    active = scrapy.Field()
    vote = scrapy.Field()
    star = scrapy.Field()
    content = scrapy.Field()
    status = scrapy.Field()
    tags = scrapy.Field()
    users = scrapy.Field()
    comments = scrapy.Field()

class Answer(scrapy.Item):
    # answer
    id = scrapy.Field()
    vote = scrapy.Field()
    accepted = scrapy.Field()
    content = scrapy.Field()
    users = scrapy.Field()
    comments = scrapy.Field()

class User(scrapy.Item):
    # user
    action = scrapy.Field()
    time = scrapy.Field()
    name = scrapy.Field()
    link = scrapy.Field()
    is_owner = scrapy.Field()
    revision = scrapy.Field()
    reputation = scrapy.Field()
    gold = scrapy.Field()
    silver = scrapy.Field()
    bronze = scrapy.Field()

class Comment(scrapy.Item):
    # comment
    score = scrapy.Field()
    content = scrapy.Field()
    user = scrapy.Field()
    user_href = scrapy.Field()
    date = scrapy.Field()

class LinkedQuestion(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    link = scrapy.Field()
    vote = scrapy.Field()
    accepted = scrapy.Field()

class RelatedQuestion(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    link = scrapy.Field()
    vote = scrapy.Field()
    accepted = scrapy.Field()

class QuestionAnswers(scrapy.Item):
    question = scrapy.Field()
    answers = scrapy.Field()
    linked_questions = scrapy.Field()
    related_questions = scrapy.Field()
