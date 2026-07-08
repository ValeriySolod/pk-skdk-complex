"""Repository operations for the Backup & Restore module."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.modules.backup_restore.models import (
    BackupJob,
    BackupJobStatus,
    RestoreJob,
    RestoreJobStatus,
)


class BackupJobRepository:
    """Persistence operations for backup creation jobs."""

    _mutable_fields = frozenset(
        {
            "title",
            "description",
            "backup_type",
            "status",
            "storage_location",
            "storage_path",
            "artifact_name",
            "file_size_bytes",
            "checksum",
            "config",
            "result_summary",
            "metadata_json",
            "error_message",
            "updated_by_id",
            "scheduled_at",
            "started_at",
            "completed_at",
        },
    )

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, job: BackupJob) -> BackupJob:
        self.db.add(job)
        self.db.flush()
        return job

    def create_backup_job(self, job: BackupJob) -> BackupJob:
        return self.create(job)

    def get_by_id(
        self,
        job_id: int,
        *,
        include_deleted: bool = False,
    ) -> BackupJob | None:
        job = self.db.get(BackupJob, job_id)
        if job is not None and job.deleted_at is not None and not include_deleted:
            return None
        return job

    def get_by_uuid(
        self,
        job_uuid: UUID,
        *,
        include_deleted: bool = False,
    ) -> BackupJob | None:
        query = select(BackupJob).where(BackupJob.job_uuid == job_uuid)
        if not include_deleted:
            query = query.where(BackupJob.deleted_at.is_(None))
        return self.db.scalar(query)

    def list(
        self,
        *,
        title: str | None = None,
        backup_type: str | None = None,
        status: str | None = None,
        storage_location: str | None = None,
        artifact_name: str | None = None,
        checksum: str | None = None,
        created_by_id: int | None = None,
        updated_by_id: int | None = None,
        scheduled_from: datetime | None = None,
        scheduled_to: datetime | None = None,
        started_from: datetime | None = None,
        started_to: datetime | None = None,
        completed_from: datetime | None = None,
        completed_to: datetime | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[BackupJob]:
        query = self._build_query(
            title=title,
            backup_type=backup_type,
            status=status,
            storage_location=storage_location,
            artifact_name=artifact_name,
            checksum=checksum,
            created_by_id=created_by_id,
            updated_by_id=updated_by_id,
            scheduled_from=scheduled_from,
            scheduled_to=scheduled_to,
            started_from=started_from,
            started_to=started_to,
            completed_from=completed_from,
            completed_to=completed_to,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
        ).order_by(BackupJob.created_at.desc(), BackupJob.id.desc())

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return list(self.db.scalars(query).all())

    def count(
        self,
        *,
        title: str | None = None,
        backup_type: str | None = None,
        status: str | None = None,
        storage_location: str | None = None,
        artifact_name: str | None = None,
        checksum: str | None = None,
        created_by_id: int | None = None,
        updated_by_id: int | None = None,
        scheduled_from: datetime | None = None,
        scheduled_to: datetime | None = None,
        started_from: datetime | None = None,
        started_to: datetime | None = None,
        completed_from: datetime | None = None,
        completed_to: datetime | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
    ) -> int:
        query = self._build_query(
            title=title,
            backup_type=backup_type,
            status=status,
            storage_location=storage_location,
            artifact_name=artifact_name,
            checksum=checksum,
            created_by_id=created_by_id,
            updated_by_id=updated_by_id,
            scheduled_from=scheduled_from,
            scheduled_to=scheduled_to,
            started_from=started_from,
            started_to=started_to,
            completed_from=completed_from,
            completed_to=completed_to,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
        )
        return self.db.scalar(select(func.count()).select_from(query.subquery())) or 0

    def update(
        self,
        job_id: int,
        values: Mapping[str, object],
    ) -> BackupJob | None:
        job = self.get_by_id(job_id)
        if job is None:
            return None

        unsupported_fields = set(values) - self._mutable_fields
        if unsupported_fields:
            fields = ", ".join(sorted(unsupported_fields))
            raise ValueError(f"Unsupported backup job update fields: {fields}")

        for field, value in values.items():
            setattr(job, field, value)

        self.db.flush()
        return job

    def mark_status(
        self,
        job_id: int,
        status: str,
        *,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        result_summary: Mapping[str, object] | None = None,
        error_message: str | None = None,
        storage_location: str | None = None,
        storage_path: str | None = None,
        artifact_name: str | None = None,
        file_size_bytes: int | None = None,
        checksum: str | None = None,
        updated_by_id: int | None = None,
    ) -> BackupJob | None:
        values: dict[str, object] = {"status": status}

        if started_at is not None:
            values["started_at"] = started_at
        if completed_at is not None:
            values["completed_at"] = completed_at
        if result_summary is not None:
            values["result_summary"] = dict(result_summary)
        if error_message is not None:
            values["error_message"] = error_message
        if storage_location is not None:
            values["storage_location"] = storage_location
        if storage_path is not None:
            values["storage_path"] = storage_path
        if artifact_name is not None:
            values["artifact_name"] = artifact_name
        if file_size_bytes is not None:
            values["file_size_bytes"] = file_size_bytes
        if checksum is not None:
            values["checksum"] = checksum
        if updated_by_id is not None:
            values["updated_by_id"] = updated_by_id

        return self.update(job_id, values)

    def start(
        self,
        job_id: int,
        *,
        started_at: datetime | None = None,
        updated_by_id: int | None = None,
    ) -> BackupJob | None:
        return self.mark_status(
            job_id,
            BackupJobStatus.RUNNING.value,
            started_at=started_at or datetime.now(timezone.utc),
            updated_by_id=updated_by_id,
        )

    def complete(
        self,
        job_id: int,
        *,
        completed_at: datetime | None = None,
        result_summary: Mapping[str, object] | None = None,
        storage_location: str | None = None,
        storage_path: str | None = None,
        artifact_name: str | None = None,
        file_size_bytes: int | None = None,
        checksum: str | None = None,
        updated_by_id: int | None = None,
    ) -> BackupJob | None:
        return self.mark_status(
            job_id,
            BackupJobStatus.COMPLETED.value,
            completed_at=completed_at or datetime.now(timezone.utc),
            result_summary=result_summary,
            storage_location=storage_location,
            storage_path=storage_path,
            artifact_name=artifact_name,
            file_size_bytes=file_size_bytes,
            checksum=checksum,
            updated_by_id=updated_by_id,
        )

    def fail(
        self,
        job_id: int,
        *,
        error_message: str | None = None,
        completed_at: datetime | None = None,
        result_summary: Mapping[str, object] | None = None,
        updated_by_id: int | None = None,
    ) -> BackupJob | None:
        return self.mark_status(
            job_id,
            BackupJobStatus.FAILED.value,
            completed_at=completed_at or datetime.now(timezone.utc),
            result_summary=result_summary,
            error_message=error_message,
            updated_by_id=updated_by_id,
        )

    def cancel(
        self,
        job_id: int,
        *,
        completed_at: datetime | None = None,
        error_message: str | None = None,
        updated_by_id: int | None = None,
    ) -> BackupJob | None:
        return self.mark_status(
            job_id,
            BackupJobStatus.CANCELLED.value,
            completed_at=completed_at or datetime.now(timezone.utc),
            error_message=error_message,
            updated_by_id=updated_by_id,
        )

    def delete(self, job_id: int) -> bool:
        job = self.get_by_id(job_id)
        if job is None:
            return False

        job.deleted_at = datetime.now(timezone.utc)
        self.db.flush()
        return True

    def mark_deleted(self, job_id: int) -> bool:
        return self.delete(job_id)

    def exists(self, job_id: int, *, include_deleted: bool = False) -> bool:
        return self.get_by_id(job_id, include_deleted=include_deleted) is not None

    def health(self) -> bool:
        return self.db.scalar(select(1)) == 1

    def _build_query(
        self,
        *,
        title: str | None = None,
        backup_type: str | None = None,
        status: str | None = None,
        storage_location: str | None = None,
        artifact_name: str | None = None,
        checksum: str | None = None,
        created_by_id: int | None = None,
        updated_by_id: int | None = None,
        scheduled_from: datetime | None = None,
        scheduled_to: datetime | None = None,
        started_from: datetime | None = None,
        started_to: datetime | None = None,
        completed_from: datetime | None = None,
        completed_to: datetime | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
    ) -> Select[tuple[BackupJob]]:
        query = select(BackupJob)

        if not include_deleted:
            query = query.where(BackupJob.deleted_at.is_(None))
        if title is not None:
            query = query.where(BackupJob.title == title)
        if backup_type is not None:
            query = query.where(BackupJob.backup_type == backup_type)
        if status is not None:
            query = query.where(BackupJob.status == status)
        if storage_location is not None:
            query = query.where(BackupJob.storage_location == storage_location)
        if artifact_name is not None:
            query = query.where(BackupJob.artifact_name == artifact_name)
        if checksum is not None:
            query = query.where(BackupJob.checksum == checksum)
        if created_by_id is not None:
            query = query.where(BackupJob.created_by_id == created_by_id)
        if updated_by_id is not None:
            query = query.where(BackupJob.updated_by_id == updated_by_id)
        if scheduled_from is not None:
            query = query.where(BackupJob.scheduled_at >= scheduled_from)
        if scheduled_to is not None:
            query = query.where(BackupJob.scheduled_at <= scheduled_to)
        if started_from is not None:
            query = query.where(BackupJob.started_at >= started_from)
        if started_to is not None:
            query = query.where(BackupJob.started_at <= started_to)
        if completed_from is not None:
            query = query.where(BackupJob.completed_at >= completed_from)
        if completed_to is not None:
            query = query.where(BackupJob.completed_at <= completed_to)
        if created_from is not None:
            query = query.where(BackupJob.created_at >= created_from)
        if created_to is not None:
            query = query.where(BackupJob.created_at <= created_to)

        return query


class RestoreJobRepository:
    """Persistence operations for restore workflow jobs."""

    _mutable_fields = frozenset(
        {
            "backup_job_id",
            "title",
            "status",
            "restore_scope",
            "target_environment",
            "source_artifact_name",
            "source_storage_path",
            "config",
            "result_summary",
            "metadata_json",
            "error_message",
            "updated_by_id",
            "started_at",
            "completed_at",
        },
    )

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, job: RestoreJob) -> RestoreJob:
        self.db.add(job)
        self.db.flush()
        return job

    def create_restore_job(self, job: RestoreJob) -> RestoreJob:
        return self.create(job)

    def get_by_id(
        self,
        job_id: int,
        *,
        include_deleted: bool = False,
    ) -> RestoreJob | None:
        job = self.db.get(RestoreJob, job_id)
        if job is not None and job.deleted_at is not None and not include_deleted:
            return None
        return job

    def get_by_uuid(
        self,
        job_uuid: UUID,
        *,
        include_deleted: bool = False,
    ) -> RestoreJob | None:
        query = select(RestoreJob).where(RestoreJob.job_uuid == job_uuid)
        if not include_deleted:
            query = query.where(RestoreJob.deleted_at.is_(None))
        return self.db.scalar(query)

    def list(
        self,
        *,
        backup_job_id: int | None = None,
        title: str | None = None,
        status: str | None = None,
        restore_scope: str | None = None,
        target_environment: str | None = None,
        source_artifact_name: str | None = None,
        created_by_id: int | None = None,
        updated_by_id: int | None = None,
        started_from: datetime | None = None,
        started_to: datetime | None = None,
        completed_from: datetime | None = None,
        completed_to: datetime | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[RestoreJob]:
        query = self._build_query(
            backup_job_id=backup_job_id,
            title=title,
            status=status,
            restore_scope=restore_scope,
            target_environment=target_environment,
            source_artifact_name=source_artifact_name,
            created_by_id=created_by_id,
            updated_by_id=updated_by_id,
            started_from=started_from,
            started_to=started_to,
            completed_from=completed_from,
            completed_to=completed_to,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
        ).order_by(RestoreJob.created_at.desc(), RestoreJob.id.desc())

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return list(self.db.scalars(query).all())

    def count(
        self,
        *,
        backup_job_id: int | None = None,
        title: str | None = None,
        status: str | None = None,
        restore_scope: str | None = None,
        target_environment: str | None = None,
        source_artifact_name: str | None = None,
        created_by_id: int | None = None,
        updated_by_id: int | None = None,
        started_from: datetime | None = None,
        started_to: datetime | None = None,
        completed_from: datetime | None = None,
        completed_to: datetime | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
    ) -> int:
        query = self._build_query(
            backup_job_id=backup_job_id,
            title=title,
            status=status,
            restore_scope=restore_scope,
            target_environment=target_environment,
            source_artifact_name=source_artifact_name,
            created_by_id=created_by_id,
            updated_by_id=updated_by_id,
            started_from=started_from,
            started_to=started_to,
            completed_from=completed_from,
            completed_to=completed_to,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
        )
        return self.db.scalar(select(func.count()).select_from(query.subquery())) or 0

    def update(
        self,
        job_id: int,
        values: Mapping[str, object],
    ) -> RestoreJob | None:
        job = self.get_by_id(job_id)
        if job is None:
            return None

        unsupported_fields = set(values) - self._mutable_fields
        if unsupported_fields:
            fields = ", ".join(sorted(unsupported_fields))
            raise ValueError(f"Unsupported restore job update fields: {fields}")

        for field, value in values.items():
            setattr(job, field, value)

        self.db.flush()
        return job

    def mark_status(
        self,
        job_id: int,
        status: str,
        *,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        result_summary: Mapping[str, object] | None = None,
        error_message: str | None = None,
        updated_by_id: int | None = None,
    ) -> RestoreJob | None:
        values: dict[str, object] = {"status": status}

        if started_at is not None:
            values["started_at"] = started_at
        if completed_at is not None:
            values["completed_at"] = completed_at
        if result_summary is not None:
            values["result_summary"] = dict(result_summary)
        if error_message is not None:
            values["error_message"] = error_message
        if updated_by_id is not None:
            values["updated_by_id"] = updated_by_id

        return self.update(job_id, values)

    def start(
        self,
        job_id: int,
        *,
        started_at: datetime | None = None,
        updated_by_id: int | None = None,
    ) -> RestoreJob | None:
        return self.mark_status(
            job_id,
            RestoreJobStatus.RUNNING.value,
            started_at=started_at or datetime.now(timezone.utc),
            updated_by_id=updated_by_id,
        )

    def complete(
        self,
        job_id: int,
        *,
        completed_at: datetime | None = None,
        result_summary: Mapping[str, object] | None = None,
        updated_by_id: int | None = None,
    ) -> RestoreJob | None:
        return self.mark_status(
            job_id,
            RestoreJobStatus.COMPLETED.value,
            completed_at=completed_at or datetime.now(timezone.utc),
            result_summary=result_summary,
            updated_by_id=updated_by_id,
        )

    def fail(
        self,
        job_id: int,
        *,
        error_message: str | None = None,
        completed_at: datetime | None = None,
        result_summary: Mapping[str, object] | None = None,
        updated_by_id: int | None = None,
    ) -> RestoreJob | None:
        return self.mark_status(
            job_id,
            RestoreJobStatus.FAILED.value,
            completed_at=completed_at or datetime.now(timezone.utc),
            result_summary=result_summary,
            error_message=error_message,
            updated_by_id=updated_by_id,
        )

    def cancel(
        self,
        job_id: int,
        *,
        completed_at: datetime | None = None,
        error_message: str | None = None,
        updated_by_id: int | None = None,
    ) -> RestoreJob | None:
        return self.mark_status(
            job_id,
            RestoreJobStatus.CANCELLED.value,
            completed_at=completed_at or datetime.now(timezone.utc),
            error_message=error_message,
            updated_by_id=updated_by_id,
        )

    def delete(self, job_id: int) -> bool:
        job = self.get_by_id(job_id)
        if job is None:
            return False

        job.deleted_at = datetime.now(timezone.utc)
        self.db.flush()
        return True

    def mark_deleted(self, job_id: int) -> bool:
        return self.delete(job_id)

    def exists(self, job_id: int, *, include_deleted: bool = False) -> bool:
        return self.get_by_id(job_id, include_deleted=include_deleted) is not None

    def health(self) -> bool:
        return self.db.scalar(select(1)) == 1

    def _build_query(
        self,
        *,
        backup_job_id: int | None = None,
        title: str | None = None,
        status: str | None = None,
        restore_scope: str | None = None,
        target_environment: str | None = None,
        source_artifact_name: str | None = None,
        created_by_id: int | None = None,
        updated_by_id: int | None = None,
        started_from: datetime | None = None,
        started_to: datetime | None = None,
        completed_from: datetime | None = None,
        completed_to: datetime | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
    ) -> Select[tuple[RestoreJob]]:
        query = select(RestoreJob)

        if not include_deleted:
            query = query.where(RestoreJob.deleted_at.is_(None))
        if backup_job_id is not None:
            query = query.where(RestoreJob.backup_job_id == backup_job_id)
        if title is not None:
            query = query.where(RestoreJob.title == title)
        if status is not None:
            query = query.where(RestoreJob.status == status)
        if restore_scope is not None:
            query = query.where(RestoreJob.restore_scope == restore_scope)
        if target_environment is not None:
            query = query.where(RestoreJob.target_environment == target_environment)
        if source_artifact_name is not None:
            query = query.where(RestoreJob.source_artifact_name == source_artifact_name)
        if created_by_id is not None:
            query = query.where(RestoreJob.created_by_id == created_by_id)
        if updated_by_id is not None:
            query = query.where(RestoreJob.updated_by_id == updated_by_id)
        if started_from is not None:
            query = query.where(RestoreJob.started_at >= started_from)
        if started_to is not None:
            query = query.where(RestoreJob.started_at <= started_to)
        if completed_from is not None:
            query = query.where(RestoreJob.completed_at >= completed_from)
        if completed_to is not None:
            query = query.where(RestoreJob.completed_at <= completed_to)
        if created_from is not None:
            query = query.where(RestoreJob.created_at >= created_from)
        if created_to is not None:
            query = query.where(RestoreJob.created_at <= created_to)

        return query


class BackupRestoreRepository:
    """Persistence boundary for backup and restore workflows."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.backup_jobs = BackupJobRepository(db)
        self.restore_jobs = RestoreJobRepository(db)

    def health(self) -> bool:
        """Return whether all backup/restore persistence boundaries are available."""
        return self.backup_jobs.health() and self.restore_jobs.health()

    def health_check(self) -> bool:
        return self.health()


__all__ = [
    "BackupJobRepository",
    "BackupRestoreRepository",
    "RestoreJobRepository",
]
