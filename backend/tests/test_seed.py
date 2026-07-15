from __future__ import annotations

import pytest
from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app import seed


class FakeSession:
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False
        self.closed = False
        self.events: list[str] = []

    def commit(self) -> None:
        self.committed = True
        self.events.append("commit")

    def rollback(self) -> None:
        self.rolled_back = True
        self.events.append("rollback")

    def close(self) -> None:
        self.closed = True
        self.events.append("close")


def test_run_seed_operations_executes_provided_operations_in_order() -> None:
    session = FakeSession()

    def first_operation(current_session: FakeSession) -> None:
        current_session.events.append("first")

    def second_operation(current_session: FakeSession) -> None:
        current_session.events.append("second")

    seed.run_seed_operations(
        session,
        operations=(first_operation, second_operation),
    )

    assert session.events == ["first", "second"]


def test_seed_database_commits_and_closes_when_operations_succeed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = FakeSession()

    def run_seed_operations(current_session: FakeSession) -> None:
        current_session.events.append("seed")

    monkeypatch.setattr(seed, "run_seed_operations", run_seed_operations)

    seed.seed_database(session_factory=lambda: session)

    assert session.committed is True
    assert session.rolled_back is False
    assert session.closed is True
    assert session.events == ["seed", "commit", "close"]


def test_seed_database_rolls_back_closes_and_reraises_operation_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = FakeSession()
    expected_error = RuntimeError("seed failed")

    def run_seed_operations(current_session: FakeSession) -> None:
        current_session.events.append("seed")
        raise expected_error

    monkeypatch.setattr(seed, "run_seed_operations", run_seed_operations)

    with pytest.raises(RuntimeError) as error:
        seed.seed_database(session_factory=lambda: session)

    assert error.value is expected_error
    assert session.committed is False
    assert session.rolled_back is True
    assert session.closed is True
    assert session.events == ["seed", "rollback", "close"]


def test_seed_database_commits_and_closes_with_empty_operation_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = FakeSession()
    original_run_seed_operations = seed.run_seed_operations

    def run_empty_seed_operations(current_session: FakeSession) -> None:
        original_run_seed_operations(current_session, operations=())

    monkeypatch.setattr(seed, "run_seed_operations", run_empty_seed_operations)

    seed.seed_database(session_factory=lambda: session)

    assert session.committed is True
    assert session.rolled_back is False
    assert session.closed is True
    assert session.events == ["commit", "close"]


def test_seed_database_can_repeat_an_idempotent_operation(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    metadata = MetaData()
    seed_entries = Table(
        "test_seed_entries",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("key", String(80), nullable=False, unique=True),
        Column("value", String(255), nullable=False),
    )
    engine = create_engine(f"sqlite+pysqlite:///{tmp_path / 'seed.db'}")
    metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    original_operations = seed.SEED_OPERATIONS

    def seed_default_entry(session: Session) -> None:
        existing = session.scalar(
            select(seed_entries.c.id).where(seed_entries.c.key == "default-role")
        )
        if existing is None:
            session.execute(
                seed_entries.insert().values(
                    key="default-role",
                    value="Standard application role",
                )
            )

    monkeypatch.setattr(seed, "SEED_OPERATIONS", (seed_default_entry,))
    try:
        seed.seed_database(session_factory=session_factory)

        with session_factory() as session:
            rows_after_first_run = session.execute(
                select(seed_entries.c.key, seed_entries.c.value)
            ).all()
        assert rows_after_first_run == [
            ("default-role", "Standard application role")
        ]

        seed.seed_database(session_factory=session_factory)

        with session_factory() as session:
            rows_after_second_run = session.execute(
                select(seed_entries.c.key, seed_entries.c.value)
            ).all()
        assert rows_after_second_run == [
            ("default-role", "Standard application role")
        ]
    finally:
        seed.SEED_OPERATIONS = original_operations
        engine.dispose()
