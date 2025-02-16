from unittest.mock import ANY

import pytest
from clickhouse_connect.driver import Client
from django.conf import settings

from users.use_cases import CreateEventOutbox, CreateEventOutboxRequest, UserCreated
from users.tasks import process_outbox_entries

pytestmark = [pytest.mark.django_db]


@pytest.fixture()
def f_use_case() -> CreateEventOutbox:
    return CreateEventOutbox()


def test_event_box_created(f_use_case: CreateEventOutbox) -> None:
    request = CreateEventOutboxRequest(event_type='user_created',
                                       environment=settings.ENVIRONMENT,
                                       event_context=UserCreated(
                                           email='test@email.com',
                                           first_name='Test',
                                           last_name='Testovich',
                                       ).model_dump(), )

    response = f_use_case.execute(request)

    assert response.result.event_type == 'user_created'
    assert response.error == ''


def test_process_outbox_entries(f_ch_client: Client):
    for i in range(1000):
        CreateEventOutboxRequest(event_type='user_created',
                                 environment=settings.ENVIRONMENT,
                                 event_context=UserCreated(
                                     email='test@email.com',
                                     first_name='Test',
                                     last_name='Testovich',
                                 ).model_dump(), )

    process_outbox_entries.delay()
    log = f_ch_client.query("SELECT * FROM default.event_log WHERE event_type = 'user_created'")

    assert log.result_rows == [
        (
            'user_created',
            ANY,
            'Local',
            '{"email": "test@email.com", "first_name": "Test", "last_name": "Testovich"}',
            1,
        ),
    ]
