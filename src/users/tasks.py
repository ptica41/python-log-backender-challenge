import structlog
from celery import shared_task

from .models import EventOutbox
from core.event_log_client import EventLogClient
from users.use_cases import EventOutboxCreated

logger = structlog.get_logger(__name__)


@shared_task
def process_outbox_entries():
    entries = EventOutbox.objects.filter(status="PENDING")

    if entries.count() < 1000:  # отправляем пакетами не менее 1000 строк
        return

    events = []
    for entry in entries:
        events.append(EventOutboxCreated(
            event_type=entry.event_type,
            event_date_time=entry.event_date_time,
            environment=entry.environment,
            event_context=entry.event_context,
            metadata_version=entry.metadata_version,
        ))

    try:
        with EventLogClient.init() as client:
            client.insert(events)
        entries.update(status="PROCESSED")
        logger.info('Success insert into ClickHouse')
    except Exception as e:
        entries.update(status="FAILED")
        raise
