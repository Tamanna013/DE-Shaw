import factory
import random
from faker import Faker
from datetime import datetime, timezone
from shared.db.base import generate_uuid
from shared.db.models.users import UserModel, BlockedEmailDomainModel
from shared.db.models.teams import TeamModel, UserProfileModel
from shared.db.models.repositories import RepositoryModel
from shared.db.models.test_runs import TestRunModel
from shared.db.models.test_cases import TestCaseModel
from shared.db.models.test_case_executions import TestCaseExecutionModel
from shared.db.models.failures import FailureModel
from shared.db.models.commits import CommitModel
from shared.db.session import async_session_maker

fake = Faker()

class AsyncSQLAlchemyModelFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = None # Needs to be bound before use in async tests
        sqlalchemy_session_persistence = 'commit'

class UserFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = UserModel

    id = factory.LazyFunction(generate_uuid)
    email = factory.Faker('email')
    full_name = factory.Faker('name')
    hashed_password = "hashed_password"

class TeamFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = TeamModel

    id = factory.LazyFunction(generate_uuid)
    name = factory.Faker('company')
    description = factory.Faker('catch_phrase')

class RepositoryFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = RepositoryModel

    id = factory.LazyFunction(generate_uuid)
    name = factory.Faker('slug')
    git_url = factory.LazyAttribute(lambda o: f"https://github.com/org/{o.name}")
    provider = "github"
    default_branch = "main"

class CommitFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = CommitModel

    id = factory.LazyFunction(generate_uuid)
    repository_id = factory.SubFactory(RepositoryFactory)
    sha = factory.Faker('sha1')
    author_email = factory.Faker('email')
    message = factory.Faker('sentence')
    authored_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    files_changed = factory.LazyAttribute(lambda _: {"modified": [f"src/{fake.word()}.py"]})

class TestRunFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = TestRunModel

    id = factory.LazyFunction(generate_uuid)
    repository_id = factory.SubFactory(RepositoryFactory)
    commit_sha = factory.Faker('sha1')
    branch = "main"
    trigger = "push"
    started_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    status = "completed"
    ci_provider = "github_actions"

class TestCaseFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = TestCaseModel

    id = factory.LazyFunction(generate_uuid)
    repository_id = factory.SubFactory(RepositoryFactory)
    qualified_name = factory.LazyAttribute(lambda o: f"tests.test_{fake.word()}::Test{fake.word().capitalize()}::test_{fake.word()}")
    file_path = factory.LazyAttribute(lambda _: f"tests/test_{fake.word()}.py")

class TestCaseExecutionFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = TestCaseExecutionModel

    id = factory.LazyFunction(generate_uuid)
    test_run_id = factory.SubFactory(TestRunFactory)
    test_case_id = factory.SubFactory(TestCaseFactory)
    status = factory.Iterator(["passed", "failed", "skipped"])
    duration_ms = factory.LazyFunction(lambda: random.randint(10, 5000))

def generate_realistic_traceback() -> str:
    tb_type = random.choice(["python", "java", "js"])
    if tb_type == "python":
        return f"Traceback (most recent call last):\n  File \"{fake.file_path()}\", line {random.randint(10, 200)}, in <module>\n    raise ValueError(\"Invalid argument\")\nValueError: Invalid argument"
    elif tb_type == "java":
        return f"java.lang.NullPointerException\n\tat com.example.{fake.word().capitalize()}.method({fake.word().capitalize()}.java:{random.randint(10, 200)})\n\tat org.junit.runners.ParentRunner$3.run(ParentRunner.java:290)"
    else:
        return f"TypeError: Cannot read properties of undefined (reading '{fake.word()}')\n    at {fake.word()} (/app/src/{fake.word()}.js:{random.randint(10, 100)}:{random.randint(1, 50)})"

class FailureFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = FailureModel

    id = factory.LazyFunction(generate_uuid)
    test_case_execution_id = factory.SubFactory(TestCaseExecutionFactory)
    error_type = factory.Iterator(["ValueError", "NullPointerException", "TypeError", "AssertionError"])
    error_message = factory.Faker('sentence')
    stack_trace_raw = factory.LazyFunction(generate_realistic_traceback)
    normalized_signature = factory.Faker('md5')
