from django.contrib import admin
from .models import Question, Answer, Tag, QuestionLike, AnswerLike


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    raw_id_fields = ("author",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "created_at")
    search_fields = ("title", "text", "author__username")
    list_filter = ("created_at",)
    list_select_related = ("author",)
    raw_id_fields = ("author",)
    inlines = (AnswerInline,)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "author", "created_at", "is_correct")
    search_fields = (
        "text",
        "question__title",
        "author__username",
    )
    list_filter = ("created_at", "is_correct")
    list_select_related = ("question", "author")
    raw_id_fields = ("question", "author")


class TagUsageFilter(admin.SimpleListFilter):
    title = "Использование тега"
    parameter_name = "used"

    def lookups(self, request, model_admin):
        return [
            ("yes", "Есть вопросы"),
            ("no", "Нет вопросов"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(
                questions__isnull = False
            ).distinct()

        if self.value() == "no":
            return queryset.filter(
                questions__isnull=True
            )
        return queryset


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    search_fields = ("name", "slug")
    ordering = ("name",)
    list_filter = (TagUsageFilter,)


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "question", "value")

    search_fields = (
        "user__username",
        "question__title",
    )

    list_filter = ("value",)

    list_select_related = ("user", "question")

    raw_id_fields = ("user", "question")


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "answer", "value")

    search_fields = (
        "user__username",
        "answer__text",
    )

    list_filter = ("value",)

    list_select_related = ("user", "answer")

    raw_id_fields = ("user", "answer")