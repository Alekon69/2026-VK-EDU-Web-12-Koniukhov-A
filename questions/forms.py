
from django import forms
from .models import Question, Tag, Answer, QuestionLike, AnswerLike
from django.utils.text import slugify
from uuid import uuid4
from django.db import transaction


class QuestionForm(forms.ModelForm):
    tags_text = forms.CharField(
        label="Теги",
        help_text="Введите теги через запятую"
    )

    class Meta:
        model = Question
        fields = ("title", "text")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["title"].widget.attrs["class"] = "text-of-title-of-new-question"
        self.fields["text"].widget.attrs["class"] = "text-of-text-of-new-question"
        self.fields["tags_text"].widget.attrs["class"] = "text-of-tags-of-new-question"



    def clean_tags_text(self):
        text = self.cleaned_data["tags_text"]
        tags = []

        for tag in text.split(","):
            tag = tag.strip()

            if tag:
                if len(tag) > 20:
                    raise forms.ValidationError(
                        "Название тега не должно превышать 20 символов."
                    )

                tags.append(tag)

        if len(tags) > 3:
            raise forms.ValidationError(
                "Можно указать не более 3 тегов."
            )

        if not tags:
            raise forms.ValidationError(
                "Укажите хотя бы один тег."
            )

        return tags


    def save(self, author):
        question = super().save(commit=False)
        question.author = author
        question.save()

        for name in self.cleaned_data["tags_text"]:
            slug = slugify(name) or "tag"

            if Tag.objects.filter(slug=slug).exclude(name=name).exists():
                slug = f"{slug}-{uuid4().hex[:4]}"

            tag, created = Tag.objects.get_or_create(
                name=name,
                defaults={"slug": slug}
            )

            question.tags.add(tag)

        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ("text",)
        widgets = {
            "text": forms.Textarea(attrs={
                "class": "enter-answer"
            })
        }

    def save(self, question, author):
        answer = super().save(commit=False)
        answer.question = question
        answer.author = author
        answer.save()
        return answer



class VoteForm(forms.Form):
    value = forms.TypedChoiceField(
        choices=[
            (1, "Лайк"),
            (-1, "Дизлайк")
        ],
        coerce=int,
        error_messages={
            "required": "Не указана оценка",
            "invalid_choice": "Допустимы только 1 и -1"
        }
    )

    def save(self, user, target):
        value = self.cleaned_data["value"]

        if isinstance(target, Question):
            vote, created = QuestionLike.objects.get_or_create(
                user=user,
                question=target,
                defaults={"value": value}
            )

        elif isinstance(target, Answer):
            vote, created = AnswerLike.objects.get_or_create(
                user=user,
                answer=target,
                defaults={"value": value}
            )

        else:
            raise ValueError("Можно оценивать только вопросы и ответы")

        if created:
            current_vote = value

        elif vote.value == value:
            vote.delete()
            current_vote = 0

        else:
            vote.value = value
            vote.save(update_fields=["value"])
            current_vote = value

        return current_vote



class CorrectAnswerForm(forms.Form):

    question_id = forms.IntegerField(min_value=1)

    def __init__(self, *args, user, answer, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.answer = answer

    
    def clean(self):
        cleaned_data = super().clean()

        question_id = cleaned_data.get("question_id")

        if question_id is not None:
            if question_id != self.answer.question_id:
                raise forms.ValidationError(
                    "Ответ не принадлежит указанному вопросу"
                )

        if self.answer.question.author_id != self.user.id:
            raise forms.ValidationError(
                "Только автор вопроса может выбрать правильный ответ"
            )

        return cleaned_data


    def save(self):
        with transaction.atomic():
            new_status = not self.answer.is_correct

            if new_status:
                Answer.objects.filter(
                    question_id=self.answer.question_id,
                    is_correct=True
                ).exclude(
                    pk=self.answer.id
                ).update(is_correct=False)

            self.answer.is_correct = new_status
            self.answer.save(update_fields=["is_correct"])

        return self.answer
