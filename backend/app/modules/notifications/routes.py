from typing import NoReturn
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.models import User
from app.modules.notifications.models import Notification, NotificationDelivery
from app.modules.notifications.repository import NotificationsRepository
from app.modules.notifications.schemas import (
    NotificationCreate,
    NotificationDeliveryCreate,
    NotificationDeliveryFilterParams,
    NotificationDeliveryListResponse,
    NotificationDeliveryResponse,
    NotificationFilterParams,
    NotificationListResponse,
    NotificationResponse,
    NotificationsHealthRead,
)
from app.modules.notifications.service import NotificationsService


router = APIRouter()


def get_notifications_service(
    db: Session = Depends(get_db),
) -> NotificationsService:
    repository = NotificationsRepository(db)
    return NotificationsService(repository)


def raise_not_found(detail: str) -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail,
    )


@router.get("/health", response_model=NotificationsHealthRead)
def module_health(
    service: NotificationsService = Depends(get_notifications_service),
    _: User = Depends(get_current_user),
) -> dict[str, str]:
    return service.health()


@router.get("", response_model=NotificationListResponse)
def list_notifications(
    filters: NotificationFilterParams = Depends(),
    service: NotificationsService = Depends(get_notifications_service),
    _: User = Depends(get_current_user),
) -> NotificationListResponse:
    filter_values = filters.model_dump()
    notifications = service.list_notifications(**filter_values)
    total = service.count_notifications(
        **{
            key: value
            for key, value in filter_values.items()
            if key not in {"limit", "offset"}
        },
    )
    return NotificationListResponse(
        items=notifications,
        total=total,
        limit=filters.limit,
        offset=filters.offset,
    )


@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_notification(
    payload: NotificationCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Notification:
    service = get_notifications_service(db)
    notification = service.create_notification(Notification(**payload.model_dump()))
    db.commit()
    db.refresh(notification)
    return notification


@router.get("/deliveries", response_model=NotificationDeliveryListResponse)
def list_notification_deliveries(
    filters: NotificationDeliveryFilterParams = Depends(),
    service: NotificationsService = Depends(get_notifications_service),
    _: User = Depends(get_current_user),
) -> NotificationDeliveryListResponse:
    filter_values = filters.model_dump()
    deliveries = service.list_deliveries(**filter_values)
    total = service.count_deliveries(
        **{
            key: value
            for key, value in filter_values.items()
            if key not in {"limit", "offset"}
        },
    )
    return NotificationDeliveryListResponse(
        items=deliveries,
        total=total,
        limit=filters.limit,
        offset=filters.offset,
    )


@router.post(
    "/deliveries",
    response_model=NotificationDeliveryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_notification_delivery(
    payload: NotificationDeliveryCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> NotificationDelivery:
    service = get_notifications_service(db)
    delivery = service.create_delivery(NotificationDelivery(**payload.model_dump()))
    db.commit()
    db.refresh(delivery)
    return delivery


@router.get(
    "/deliveries/uuid/{delivery_uuid}",
    response_model=NotificationDeliveryResponse,
)
def get_notification_delivery_by_uuid(
    delivery_uuid: UUID,
    service: NotificationsService = Depends(get_notifications_service),
    _: User = Depends(get_current_user),
) -> NotificationDelivery:
    delivery = service.get_delivery_by_uuid(delivery_uuid)
    if delivery is None:
        raise_not_found("Notification delivery not found")
    return delivery


@router.get("/deliveries/{delivery_id}", response_model=NotificationDeliveryResponse)
def get_notification_delivery(
    delivery_id: int,
    service: NotificationsService = Depends(get_notifications_service),
    _: User = Depends(get_current_user),
) -> NotificationDelivery:
    delivery = service.get_delivery(delivery_id)
    if delivery is None:
        raise_not_found("Notification delivery not found")
    return delivery


@router.get("/uuid/{notification_uuid}", response_model=NotificationResponse)
def get_notification_by_uuid(
    notification_uuid: UUID,
    service: NotificationsService = Depends(get_notifications_service),
    _: User = Depends(get_current_user),
) -> Notification:
    notification = service.get_notification_by_uuid(notification_uuid)
    if notification is None:
        raise_not_found("Notification not found")
    return notification


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: int,
    service: NotificationsService = Depends(get_notifications_service),
    _: User = Depends(get_current_user),
) -> Notification:
    notification = service.get_notification(notification_id)
    if notification is None:
        raise_not_found("Notification not found")
    return notification
