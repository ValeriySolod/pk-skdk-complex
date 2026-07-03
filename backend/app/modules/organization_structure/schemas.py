from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class OrganizationUnitBase(BaseModel):
    name: str
    code: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: bool = True


class OrganizationUnitCreate(OrganizationUnitBase):
    pass


class OrganizationUnitUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None


class OrganizationUnitRead(OrganizationUnitBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class PositionBase(BaseModel):
    title: str
    code: Optional[str] = None
    organization_unit_id: int
    is_active: bool = True


class PositionCreate(PositionBase):
    pass


class PositionUpdate(BaseModel):
    title: Optional[str] = None
    code: Optional[str] = None
    organization_unit_id: Optional[int] = None
    is_active: Optional[bool] = None


class PositionRead(PositionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class EmployeeAssignmentBase(BaseModel):
    user_id: int
    position_id: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: bool = True


class EmployeeAssignmentCreate(EmployeeAssignmentBase):
    pass


class EmployeeAssignmentUpdate(BaseModel):
    user_id: Optional[int] = None
    position_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None


class EmployeeAssignmentRead(EmployeeAssignmentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
