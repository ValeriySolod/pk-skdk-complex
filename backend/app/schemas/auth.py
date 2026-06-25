from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class UserRead(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
    department: str | None = None
    is_active: bool

    model_config = {'from_attributes': True}
