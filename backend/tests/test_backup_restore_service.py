from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest

from app.modules.backup_restore.models import (
    BackupJob,
    BackupJobStatus,
    BackupJobType,
    RestoreJob,
    RestoreJobStatus,
)
from app.modules.backup_restore.service import BackupRestoreService


class FakeBackupJobRepository:
    def __init__(self, *, healthy: bool = True) -> None:
        self.healthy = healthy
        self.jobs: list[BackupJob] = []
        self.calls: list[tuple[str, dict[str, object]]] = []

    def create_backup_job(self, job: BackupJob) -> BackupJob:
        self.calls.append(("create_backup_job", {"job": job}))
        if job.id is None:
            job.id = len(self.jobs) + 1
        self.jobs.append(job)
        return job

    def get_by_id(
        self,
        job_id: int,
        *,
        include_deleted: bool = False,
    ) -> BackupJob | None:
        self.calls.append(
            (
                "get_by_id",
                {"job_id": job_id, "include_deleted": include_deleted},
            )
        )
        return next((job for job in self.jobs if job.id == job_id), None)

    def get_by_uuid(
        self,
        job_uuid: object,
        *,
        include_deleted: bool = False,
    ) -> BackupJob | None:
        self.calls.append(
            (
                "get_by_uuid",
                {"job_uuid": job_uuid, "include_deleted": include_deleted},
            )
        )
        return next((job for job in self.jobs if job.job_uuid == job_uuid), None)

    def list(self, **filters: object) -> list[BackupJob]:
        self.calls.append(("list", filters))
        return list(self.jobs)

    def count(self, **filters: object) -> int:
        self.calls.append(("count", filters))
        status = filters.get("status")
        backup_type = filters.get("backup_type")
        return sum(
            1
            for job in self.jobs
            if (status is None or job.status == status)
            and (backup_type is None or job.backup_type == backup_type)
        )

    def update(
        self,
        job_id: int,
        values: object,
    ) -> BackupJob | None:
        self.calls.append(("update", {"job_id": job_id, "values": values}))
        job = next((item for item in self.jobs if item.id == job_id), None)
        if job is None:
            return None
        for key, value in dict(values).items():
            setattr(job, key, value)
        return job

    def mark_status(
        self,
        job_id: int,
        status: str,
        **values: object,
    ) -> BackupJob | None:
        self.calls.append(
            ("mark_status", {"job_id": job_id, "status": status, **values})
        )
        return self.update(job_id, {"status": status, **values})

    def health(self) -> bool:
        self.calls.append(("health", {}))
        return self.healthy


class FakeRestoreJobRepository:
    def __init__(self, *, healthy: bool = True) -> None:
        self.healthy = healthy
        self.jobs: list[RestoreJob] = []
        self.calls: list[tuple[str, dict[str, object]]] = []

    def create_restore_job(self, job: RestoreJob) -> RestoreJob:
        self.calls.append(("create_restore_job", {"job": job}))
        if job.id is None:
            job.id = len(self.jobs) + 1
        self.jobs.append(job)
        return job

    def get_by_id(
        self,
        job_id: int,
        *,
        include_deleted: bool = False,
    ) -> RestoreJob | None:
        self.calls.append(
            (
                "get_by_id",
                {"job_id": job_id, "include_deleted": include_deleted},
            )
        )
        return next((job for job in self.jobs if job.id == job_id), None)

    def get_by_uuid(
        self,
        job_uuid: object,
        *,
        include_deleted: bool = False,
    ) -> RestoreJob | None:
        self.calls.append(
            (
                "get_by_uuid",
                {"job_uuid": job_uuid, "include_deleted": include_deleted},
            )
        )
        return next((job for job in self.jobs if job.job_uuid == job_uuid), None)

    def list(self, **filters: object) -> list[RestoreJob]:
        self.calls.append(("list", filters))
        return list(self.jobs)

    def count(self, **filters: object) -> int:
        self.calls.append(("count", filters))
        status = filters.get("status")
        return sum(1 for job in self.jobs if status is None or job.status == status)

    def update(
        self,
        job_id: int,
        values: object,
    ) -> RestoreJob | None:
        self.calls.append(("update", {"job_id": job_id, "values": values}))
        job = next((item for item in self.jobs if item.id == job_id), None)
        if job is None:
            return None
        for key, value in dict(values).items():
            setattr(job, key, value)
        return job

    def mark_status(
        self,
        job_id: int,
        status: str,
        **values: object,
    ) -> RestoreJob | None:
        self.calls.append(
            ("mark_status", {"job_id": job_id, "status": status, **values})
        )
        return self.update(job_id, {"status": status, **values})

    def health(self) -> bool:
        self.calls.append(("health", {}))
        return self.healthy


class FakeBackupRestoreRepository:
    def __init__(
        self,
        backup_jobs: FakeBackupJobRepository,
        restore_jobs: FakeRestoreJobRepository,
    ) -> None:
        self.backup_jobs = backup_jobs
        self.restore_jobs = restore_jobs


@pytest.fixture()
def backup_repository() -> FakeBackupJobRepository:
    return FakeBackupJobRepository()


@pytest.fixture()
def restore_repository() -> FakeRestoreJobRepository:
    return FakeRestoreJobRepository()


@pytest.fixture()
def service(
    backup_repository: FakeBackupJobRepository,
    restore_repository: FakeRestoreJobRepository,
) -> BackupRestoreService:
    return BackupRestoreService(
        backup_jobs=backup_repository,
        restore_jobs=restore_repository,
    )


def test_service_initializes_with_injected_repositories(
    backup_repository: FakeBackupJobRepository,
    restore_repository: FakeRestoreJobRepository,
) -> None:
    service = BackupRestoreService(
        repository=FakeBackupRestoreRepository(backup_repository, restore_repository),
    )

    assert service.backup_jobs is backup_repository
    assert service.restore_jobs is restore_repository
    assert service.health().model_dump() == {
        "module": "backup_restore",
        "status": "ok",
    }


def test_service_requires_repository_or_db_session() -> None:
    with pytest.raises(ValueError, match="requires a repository"):
        BackupRestoreService()


def test_backup_job_crud_delegates_to_repository(
    service: BackupRestoreService,
    backup_repository: FakeBackupJobRepository,
) -> None:
    created_at = datetime(2026, 7, 8, 9, 0, 0)
    job = service.create_backup_job(
        {
            "title": "Nightly backup",
            "backup_type": BackupJobType.FULL.value,
            "status": BackupJobStatus.PENDING.value,
            "created_at": created_at,
        }
    )

    assert isinstance(job, BackupJob)
    assert backup_repository.calls[0][0] == "create_backup_job"
    assert service.get_backup_job_by_id(job.id, include_deleted=True) is job
    assert service.get_backup_job_by_uuid(job.job_uuid) is job
    assert service.list_backup_jobs(status=BackupJobStatus.PENDING.value) == [job]
    assert service.count_backup_jobs(backup_type=BackupJobType.FULL.value) == 1

    updated = service.update_backup_job(
        job.id,
        {"artifact_name": "nightly.dump", "file_size_bytes": 2048},
    )

    assert updated is job
    assert job.artifact_name == "nightly.dump"
    assert job.file_size_bytes == 2048
    assert backup_repository.calls[-1] == (
        "update",
        {
            "job_id": job.id,
            "values": {"artifact_name": "nightly.dump", "file_size_bytes": 2048},
        },
    )


def test_backup_job_status_marking_delegates_to_repository(
    service: BackupRestoreService,
    backup_repository: FakeBackupJobRepository,
) -> None:
    job = service.create_backup_job(
        BackupJob(
            title="Manual backup",
            backup_type=BackupJobType.MANUAL.value,
        )
    )
    completed_at = datetime(2026, 7, 8, 10, 0, 0)

    marked = service.mark_backup_job_status(
        job.id,
        BackupJobStatus.COMPLETED.value,
        completed_at=completed_at,
        result_summary={"tables": 12},
        storage_location="local",
        storage_path="/backups/manual.dump",
        artifact_name="manual.dump",
        file_size_bytes=4096,
        checksum="sha256:test",
        updated_by_id=7,
    )

    assert marked is job
    assert job.status == BackupJobStatus.COMPLETED.value
    assert backup_repository.calls[-2][0] == "mark_status"
    assert backup_repository.calls[-2][1]["completed_at"] == completed_at
    assert backup_repository.calls[-2][1]["result_summary"] == {"tables": 12}


def test_restore_job_crud_delegates_to_repository(
    service: BackupRestoreService,
    restore_repository: FakeRestoreJobRepository,
) -> None:
    created_at = datetime(2026, 7, 8, 11, 0, 0)
    job = service.create_restore_job(
        {
            "title": "Restore staging",
            "status": RestoreJobStatus.PENDING.value,
            "restore_scope": "database",
            "target_environment": "staging",
            "created_at": created_at,
        }
    )

    assert isinstance(job, RestoreJob)
    assert restore_repository.calls[0][0] == "create_restore_job"
    assert service.get_restore_job_by_id(job.id, include_deleted=True) is job
    assert service.get_restore_job_by_uuid(job.job_uuid) is job
    assert service.list_restore_jobs(target_environment="staging") == [job]
    assert service.count_restore_jobs(status=RestoreJobStatus.PENDING.value) == 1

    updated = service.update_restore_job(
        job.id,
        {"source_artifact_name": "nightly.dump"},
    )

    assert updated is job
    assert job.source_artifact_name == "nightly.dump"
    assert restore_repository.calls[-1] == (
        "update",
        {"job_id": job.id, "values": {"source_artifact_name": "nightly.dump"}},
    )


def test_restore_job_status_marking_delegates_to_repository(
    service: BackupRestoreService,
    restore_repository: FakeRestoreJobRepository,
) -> None:
    job = service.create_restore_job(
        RestoreJob(title="Restore production", restore_scope="database")
    )
    started_at = datetime(2026, 7, 8, 12, 0, 0)

    marked = service.mark_restore_job_status(
        job.id,
        RestoreJobStatus.RUNNING.value,
        started_at=started_at,
        result_summary={"phase": "precheck"},
        updated_by_id=9,
    )

    assert marked is job
    assert job.status == RestoreJobStatus.RUNNING.value
    assert restore_repository.calls[-2][0] == "mark_status"
    assert restore_repository.calls[-2][1]["started_at"] == started_at
    assert restore_repository.calls[-2][1]["result_summary"] == {"phase": "precheck"}


def test_health_status_and_statistics_are_repository_backed(
    service: BackupRestoreService,
    backup_repository: FakeBackupJobRepository,
    restore_repository: FakeRestoreJobRepository,
) -> None:
    service.create_backup_job(
        BackupJob(
            title="Full backup",
            backup_type=BackupJobType.FULL.value,
            status=BackupJobStatus.COMPLETED.value,
        )
    )
    service.create_backup_job(
        BackupJob(
            title="Incremental backup",
            backup_type=BackupJobType.INCREMENTAL.value,
            status=BackupJobStatus.FAILED.value,
        )
    )
    service.create_restore_job(
        RestoreJob(
            title="Restore completed",
            restore_scope="database",
            status=RestoreJobStatus.COMPLETED.value,
        )
    )

    backup_statistics = service.get_backup_statistics()
    restore_statistics = service.get_restore_statistics()
    module_status = service.get_module_status()

    assert backup_statistics["total"] == 2
    assert backup_statistics["by_status"] == {
        "pending": 0,
        "running": 0,
        "completed": 1,
        "failed": 1,
        "cancelled": 0,
    }
    assert backup_statistics["by_type"] == {
        "full": 1,
        "incremental": 1,
        "manual": 0,
        "scheduled": 0,
    }
    assert restore_statistics["total"] == 1
    assert restore_statistics["by_status"] == {
        "pending": 0,
        "running": 0,
        "completed": 1,
        "failed": 0,
        "cancelled": 0,
    }
    assert module_status["module"] == "backup_restore"
    assert module_status["status"] == "ok"
    assert module_status["repositories"] == {
        "backup_jobs": True,
        "restore_jobs": True,
    }

    restore_repository.healthy = False

    assert service.health().status == "error"
    assert service.get_module_status()["repositories"] == {
        "backup_jobs": True,
        "restore_jobs": False,
    }


def test_missing_uuid_lookup_preserves_repository_semantics(
    service: BackupRestoreService,
) -> None:
    assert service.get_backup_job_by_uuid(uuid4()) is None
    assert service.get_restore_job_by_uuid(uuid4()) is None
