from dataclasses import dataclass


@dataclass(frozen=True)
class HealthCheckResult:
    """Represent a reusable health check result payload."""

    status: str
    component_key: str
    component_status: str
    detail: str | None = None

    @property
    def is_healthy(self) -> bool:
        return self.status == "ok"

    def as_response(self) -> dict[str, str]:
        response = {
            "status": self.status,
            self.component_key: self.component_status,
        }
        if self.detail is not None:
            response["detail"] = self.detail
        return response


@dataclass(frozen=True)
class ServiceHealthStatus(HealthCheckResult):
    """Describe the health state of an external or internal service."""


@dataclass(frozen=True)
class ApplicationHealthStatus:
    """Describe the top-level application health response."""

    status: str
    app: str

    @property
    def is_healthy(self) -> bool:
        return self.status == "ok"

    def as_response(self) -> dict[str, str]:
        return {"status": self.status, "app": self.app}
