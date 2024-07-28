from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Column, JSON

from scripts.core.db.psql import Base


class Categories(Base):
    __tablename__ = "categories"
    category_id: Mapped[str] = mapped_column(primary_key=True)
    category_name: Mapped[str]
    description: Mapped[str]
    meta = Column(JSON, nullable=True)


class Transactions(Base):
    __tablename__ = "transaction"
    t_id: Mapped[str] = mapped_column(primary_key=True)
    category_id: Mapped[str]
    amount: Mapped[str]
    description: Mapped[str]
    meta = Column(JSON, nullable=True)
