from datetime import datetime
from typing import Dict, Any

import structlog

from core.base_model import Model
from core.use_case import UseCase, UseCaseRequest, UseCaseResponse
from users.models import EventOutbox

logger = structlog.get_logger(__name__)


class EventOutboxCreated(Model):
    event_type: str
    event_date_time: datetime
    environment: str
    event_context: Dict[str, Any]
    metadata_version: int
    status: str


class CreateEventOutboxRequest(UseCaseRequest):
    event_type: str
    environment: str
    event_context: Dict[str, Any]
    metadata_version: int
    status: str


class CreateEventOutboxResponse(UseCaseResponse):
    result: EventOutbox | None = None
    error: str = ''


class CreateEventOutbox(UseCase):
    def _get_context_vars(self, request: UseCaseRequest) -> dict[str, Any]:
        return {
            'event_type': request.event_type,
            'environment': request.environment,
            'event_context': request.event_context,
            'metadata_version': request.metadata_version,
            'status': request.status
        }

    def _execute(self, request: CreateEventOutboxRequest) -> CreateEventOutboxResponse:
        logger.info('creating a new event outbox')

        event_outbox = EventOutbox.objects.create(
            event_type=request.event_type,
            event_date_time=request.event_date_time,
            environment=request.environment,
            event_context=request.event_context,
            metadata_version=request.metadata_version,
            status=request.status
        )

        logger.info('event outbox has been created')
        return CreateEventOutboxResponse(result=event_outbox)
