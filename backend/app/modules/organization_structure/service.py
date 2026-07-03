"""Service layer placeholder for the organization structure module."""

from app.modules.organization_structure.repository import (
    OrganizationStructureRepository,
)


class OrganizationStructureService:
    """Future business boundary for organization structure operations."""

    def __init__(self, repository: OrganizationStructureRepository) -> None:
        self.repository = repository

