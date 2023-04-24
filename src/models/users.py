from sqlalchemy.orm import Mapped, mapped_column

from ..util.database import Base


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(primary_key=True)
    email: Mapped[str]
    full_name: Mapped[str] = mapped_column(default="")
    disabled: Mapped[bool] = mapped_column(default=False)
    hashed_password: Mapped[str]
