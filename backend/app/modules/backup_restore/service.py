"""Service layer for the Backup & Restore module."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.backup_restore.models import (
    BackupJob,
    BackupJobStatus,
    BackupJobType,
    RestoreJob,
    RestoreJobStatus,
)
from app.modules.backup_restore.repository import (
    BackupJobRepository,
    BackupRestoreRepository,
    RestoreJobRepository,
)
from app.modules.backup_restore.schemas import BackupRestoreHealthRead

Payload = Mapping[str, object]


class BackupRestoreService:
    """Business boundary for backup creation and restore workflows."""

    def __init__(
        self,
        repository: BackupRestoreRepository | Session | None = None,
        *,
        backup_jobs: BackupJobRepository | None = None,
        restore_jobs: RestoreJobRepository | None = None,
        backup_job_repository: BackupJobRepository | None = None,
        restore_job_repository: RestoreJobRepository | None = None,
        db: Session | None = None,
    ) -> None:
        if isinstance(repository, Session):
            db = repository
            repository = None
        if backup_jobs is None:
            backup_jobs = backup_job_repository
        if restore_jobs is None:
            restore_jobs = restore_job_repository

        if repository is None and (backup_jobs is None or restore_jobs is None):
            if db is None:
                raise ValueError(
                    "BackupRestoreService requires a repository, injected job "
                    "repositories, or a database session."
                )
            repository = BackupRestoreRepository(db)

        self.repository = repository
        self.backup_jobs = (
            backup_jobs
            if backup_jobs is not None
            else self._require_repository().backup_jobs
        )
        self.restore_jobs = (
            restore_jobs
            if restore_jobs is not None
            else self._require_repository().restore_jobs
        )

    def health(self) -> BackupRestoreHealthRead:
        """Return aggregate Backup & Restore module health."""

        return BackupRestoreHealthRead(
            module="backup_restore",
            status="ok" if self._all_repositories_healthy() else "error",
        )

    def get_module_status(self) -> dict[str, object]:
        """Return module status with repository checks and job statistics."""

        repository_checks = self._repository_checks()
        return {
            "module": "backup_restore",
            "status": "ok" if all(repository_checks.values()) else "error",
            "repositories": repository_checks,
            "backup_statistics": self.get_backup_statistics(),
            "restore_statistics": self.get_restore_statistics(),
        }

    def get_backup_statistics(self) -> dict[str, object]:
        """Return count-based backup job statistics."""

        return {
            "total": self.count_backup_jobs(),
            "by_status": {
                status.value: self.count_backup_jobs(status=status.value)
                for status in BackupJobStatus
            },
            "by_type": {
                backup_type.value: self.count_backup_jobs(
                    backup_type=backup_type.value,
                )
                for backup_type in BackupJobType
            },
        }

    def get_restore_statistics(self) -> dict[str, object]:
        """Return count-based restore job statistics."""

        return {
            "total": self.count_restore_jobs(),
            "by_status": {
                status.value: self.count_restore_jobs(status=status.value)
                for status in RestoreJobStatus
            },
        }

    # Backup jobs

    def create_backup_job(self, payload: Payload | BackupJob) -> BackupJob:
        """Create a backup job."""

        job = payload if isinstance(payload, BackupJob) else BackupJob(**dict(payload))
        return self.backup_jobs.create_backup_job(job)

    def get_backup_job(
        self,
        job_id: int,
        *,
        include_deleted: bool = False,
    ) -> BackupJob | None:
        """Get a backup job by integer ID."""

        return self.backup_jobs.get_by_id(job_id, include_deleted=include_deleted)

    def get_backup_job_by_id(
        self,
        job_id: int,
        *,
        include_deleted: bool = False,
    ) -> BackupJob | None:
        """Get a backup job by integer ID."""

        return self.get_backup_job(job_id, include_deleted=include_deleted)

    def get_backup_job_by_uuid(
        self,
        job_uuid: UUID,
        *,
        include_deleted: bool = False,
    ) -> BackupJob | None:
        """Get a backup job by UUID."""

        return self.backup_jobs.get_by_uuid(
            job_uuid,
            include_deleted=include_deleted,
        )

    def list_backup_jobs(
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
        """List backup jobs using repository filters."""

        return self.backup_jobs.list(
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
            limit=limit,
            offset=offset,
        )

    def count_backup_jobs(
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
        """Count backup jobs using repository filters."""

        return self.backup_jobs.count(
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

    def update_backup_job(
        self,
        job_id: int,
        values: Payload,
    ) -> BackupJob | None:
        """Update mutable backup job fields."""

        return self.backup_jobs.update(job_id, values)

    def mark_backup_job_status(
        self,
        job_id: int,
        status: str,
        *,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        result_summary: Payload | None = None,
        error_message: str | None = None,
        storage_location: str | None = None,
        storage_path: str | None = None,
        artifact_name: str | None = None,
        file_size_bytes: int | None = None,
        checksum: str | None = None,
        updated_by_id: int | None = None,
    ) -> BackupJob | None:
        """Update backup job lifecycle status."""

        return self.backup_jobs.mark_status(
            job_id,
            status,
            started_at=started_at,
            completed_at=completed_at,
            result_summary=result_summary,
            error_message=error_message,
            storage_location=storage_location,
            storage_path=storage_path,
            artifact_name=artifact_name,
            file_size_bytes=file_size_bytes,
            checksum=checksum,
            updated_by_id=updated_by_id,
        )

    # Restore jobs

    def create_restore_job(self, payload: Payload | RestoreJob) -> RestoreJob:
        """Create a restore job."""

        job = payload if isinstance(payload, RestoreJob) else RestoreJob(**dict(payload))
        return self.restore_jobs.create_restore_job(job)

    def get_restore_job(
        self,
        job_id: int,
        *,
        include_deleted: bool = False,
    ) -> RestoreJob | None:
        """Get a restore job by integer ID."""

        return self.restore_jobs.get_by_id(job_id, include_deleted=include_deleted)

    def get_restore_job_by_id(
        self,
        job_id: int,
        *,
        include_deleted: bool = False,
    ) -> RestoreJob | None:
        """Get a restore job by integer ID."""

        return self.get_restore_job(job_id, include_deleted=include_deleted)

    def get_restore_job_by_uuid(
        self,
        job_uuid: UUID,
        *,
        include_deleted: bool = False,
    ) -> RestoreJob | None:
        """Get a restore job by UUID."""

        return self.restore_jobs.get_by_uuid(
            job_uuid,
            include_deleted=include_deleted,
        )

    def list_restore_jobs(
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
        """List restore jobs using repository filters."""

        return self.restore_jobs.list(
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
            limit=limit,
            offset=offset,
        )

    def count_restore_jobs(
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
        """Count restore jobs using repository filters."""

        return self.restore_jobs.count(
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

    def update_restore_job(
        self,
        job_id: int,
        values: Payload,
    ) -> RestoreJob | None:
        """Update mutable restore job fields."""

        return self.restore_jobs.update(job_id, values)

    def mark_restore_job_status(
        self,
        job_id: int,
        status: str,
        *,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        result_summary: Payload | None = None,
        error_message: str | None = None,
        updated_by_id: int | None = None,
    ) -> RestoreJob | None:
        """Update restore job lifecycle status."""

        return self.restore_jobs.mark_status(
            job_id,
            status,
            started_at=started_at,
            completed_at=completed_at,
            result_summary=result_summary,
            error_message=error_message,
            updated_by_id=updated_by_id,
        )

    # Compatibility aliases
    create = create_backup_job
    get_by_id = get_backup_job_by_id
    get_by_uuid = get_backup_job_by_uuid
    list = list_backup_jobs
    count = count_backup_jobs
    update = update_backup_job
    mark_status = mark_backup_job_status

    create_job = create_backup_job
    get_job = get_backup_job
    get_job_by_id = get_backup_job_by_id
    get_job_by_uuid = get_backup_job_by_uuid
    list_jobs = list_backup_jobs
    count_jobs = count_backup_jobs
    update_job = update_backup_job
    mark_job_status = mark_backup_job_status

    # Internal helpers

    def _require_repository(self) -> BackupRestoreRepository:
        if self.repository is None:
            raise ValueError("BackupRestoreRepository is not configured.")
        return self.repository

    def _all_repositories_healthy(self) -> bool:
        return all(self._repository_checks().values())

    def _repository_checks(self) -> dict[str, bool]:
        return {
            "backup_jobs": self._safe_health(self.backup_jobs),
            "restore_jobs": self._safe_health(self.restore_jobs),
        }

    @staticmethod
    def _safe_health(repository: object) -> bool:
        health = getattr(repository, "health", None)
        if not callable(health):
            return False
        try:
            return bool(health())
        except Exception:
            return False


__all__ = ["BackupRestoreService"]
