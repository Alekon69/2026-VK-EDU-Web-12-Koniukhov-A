from django.db import models
from django.conf import settings
from django.db.models import Count, Q, Sum



class QuestionManager(models.Manager):

    def with_stats(self):
        return (
            self.get_queryset()
            .select_related("author")
            .prefetch_related("tags")
            .annotate(
                answers_count=Count("answers", distinct=True),
                rating=(
                    Count(
                        "likes",
                        filter=Q(likes__value=1),
                        distinct=True
                    )
                    -
                    Count(
                        "likes",
                        filter=Q(likes__value=-1),
                        distinct=True
                    )
                )
            )
        )

    def newest(self):
        return self.with_stats().order_by(
            "-created_at",
            "-id"
        )

    def best(self):
        return self.with_stats().order_by(
            "-rating",
            "-created_at",
            "-id"
        )



class Question(models.Model):
    objects = QuestionManager()

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Автор"
    )

    title = models.CharField(
        max_length=255,
        verbose_name="Заголовок"
    )

    tags = models.ManyToManyField(
        "Tag",
        related_name="questions",
        blank=True,
        verbose_name="Теги"
    )

    text = models.TextField(
        verbose_name="Текст вопроса"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"


class AnswerManager(models.Manager):

    def for_question(self,question_id):
        return (
            self.get_queryset()
            .filter(question_id=question_id)
            .select_related("author")
            .annotate(
                rating=Sum("likes__value", default=0))
            .order_by("created_at", "id")
        )



class Answer(models.Model):
    objects = AnswerManager()

    is_correct = models.BooleanField(
    default=False,
    verbose_name="Правильный ответ"
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Вопрос"
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Автор"
    )

    text = models.TextField(
        verbose_name="Текст ответа"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    def __str__(self):
        return self.text[:50]

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"



class Tag(models.Model):
    name = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Название"
    )

    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="Название для URL"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"



class QuestionLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="question_likes",
        verbose_name="Пользователь"
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="Вопрос"
    )

    value = models.SmallIntegerField(
        choices=[
            (1, "Лайк"),
            (-1, "Дизлайк")
        ],
        verbose_name="Оценка"
    )

    class Meta:
        verbose_name = "Оценка вопроса"
        verbose_name_plural = "Оценки вопросов"
        unique_together = (("user", "question"),)



class AnswerLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="answer_likes",
        verbose_name="Пользователь"
    )

    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="Ответ"
    )

    value = models.SmallIntegerField(
        choices=[
            (1, "Лайк"),
            (-1, "Дизлайк")
        ],
        verbose_name="Оценка"
    )

    class Meta:
        verbose_name = "Оценка ответа"
        verbose_name_plural = "Оценки ответов"
        unique_together = (("user", "answer"),)