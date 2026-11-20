
import random
import uuid

from faker import Faker
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError

from core.models import Profile
from questions.models import (
    Question, Answer, Tag, QuestionLike, AnswerLike
)


BATCH_SIZE = 1000


def create_many(model, count, make_object, collect_ids=False):
    ids = []

    for start in range(0, count, BATCH_SIZE):
        end = min(start + BATCH_SIZE, count)

        objects = [make_object(i) for i in range(start, end)]
        created = model.objects.bulk_create(
            objects, batch_size=BATCH_SIZE
        )

        if collect_ids:
            ids.extend(obj.id for obj in created)

    return ids


class Command(BaseCommand):
    help = "Генерация тестовых данных"

    def add_arguments(self, parser):
        parser.add_argument("ratio", type=int, nargs="?", default=2)

    def handle(self, *args, **options):
        ratio = options["ratio"]

        if ratio < 2:
            raise CommandError(
                "Минимальный ratio = 2 из-за ограничения "
                "на уникальные оценки."
            )

        fake = Faker("en_US")
        User = get_user_model()
        prefix = uuid.uuid4().hex[:8]
        password = make_password("demo12345")

        users = create_many(
            User, ratio,
            lambda i: User(
                username=f"user_{prefix}_{i}",
                email=f"user_{prefix}_{i}@example.com",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                password=password
            ),
            collect_ids=True
        )

        create_many(
            Profile, ratio,
            lambda i: Profile(user_id=users[i])
        )

        tags = create_many(
            Tag, ratio,
            lambda i: Tag(
                name=f"tag_{prefix}_{i}",
                slug=f"tag-{prefix}-{i}"
            ),
            collect_ids=True
        )

        questions = create_many(
            Question, 10 * ratio,
            lambda i: Question(
                author_id=random.choice(users),
                title=fake.sentence(nb_words=6)[:255],
                text=fake.paragraph()
            ),
            collect_ids=True
        )

        Through = Question.tags.through

        create_many(
            Through, 2 * len(questions),
            lambda i: Through(
                question_id=questions[i // 2],
                tag_id=tags[(i // 2 + i % 2) % len(tags)]
            )
        )

        texts = [fake.paragraph() for _ in range(100)]

        answers = create_many(
            Answer, 100 * ratio,
            lambda i: Answer(
                question_id=random.choice(questions),
                author_id=random.choice(users),
                text=random.choice(texts),
                is_correct=random.random() < 0.05
            ),
            collect_ids=True
        )

        self.add_votes(
            QuestionLike, "question", questions, users,
            10 * ratio
        )

        self.add_votes(
            AnswerLike, "answer", answers, users,
            190 * ratio
        )

        self.stdout.write(
            self.style.SUCCESS("База успешно заполнена!")
        )

    def add_votes(self, model, field, targets, users, count):
        def make_vote(i):
            target_pos = i % len(targets)
            user_pos = (
                target_pos + i // len(targets)
            ) % len(users)

            return model(
                user_id=users[user_pos],
                value=random.choice((-1, 1)),
                **{f"{field}_id": targets[target_pos]}
            )

        create_many(model, count, make_vote)
        self.stdout.write(f"{model.__name__}: {count}")
