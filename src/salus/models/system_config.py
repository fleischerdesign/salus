from sqlmodel import Field, SQLModel


class SystemConfig(SQLModel, table=True):
    __tablename__ = "system_config"  # pyright: ignore[reportAssignmentType]

    key: str = Field(primary_key=True)
    value: str = Field(default="")
    description: str = Field(default="")
    category: str = Field(default="general")
    is_secret: bool = Field(default=False)
