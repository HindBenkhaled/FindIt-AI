"""SQLite models, sessions, and lightweight additive migrations."""
from datetime import date, datetime, timezone
from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, String, Text, create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from src.config import DATABASE_URL, DATA_DIR


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"
    __table_args__ = (CheckConstraint("report_type IN ('lost', 'found')"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    report_type: Mapped[str] = mapped_column(String(5), index=True)
    name: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(40))
    description: Mapped[str] = mapped_column(Text)
    location: Mapped[str] = mapped_column(String(200))
    location_detail: Mapped[str | None] = mapped_column(String(300), nullable=True)
    event_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    identifying_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    handover_location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    image_path: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class Claim(Base):
    __tablename__ = "claims"
    __table_args__ = (CheckConstraint("status IN ('pending', 'approved', 'rejected')"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    lost_report_id: Mapped[int] = mapped_column(ForeignKey("items.id", ondelete="CASCADE"), index=True)
    found_report_id: Mapped[int] = mapped_column(ForeignKey("items.id", ondelete="CASCADE"), index=True)
    verification_response: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(10), default="pending", index=True)
    collection_point: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    lost_item: Mapped[Item] = relationship(foreign_keys=[lost_report_id])
    found_item: Mapped[Item] = relationship(foreign_keys=[found_report_id])


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False, "timeout": 30})
SessionLocal = sessionmaker(engine, expire_on_commit=False)


def init_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(engine)
    columns = {column["name"] for column in inspect(engine).get_columns("items")}
    additions = {"location_detail": "TEXT", "identifying_details": "TEXT", "handover_location": "VARCHAR(100)"}
    with engine.begin() as connection:
        for name, sql_type in additions.items():
            if name not in columns:
                connection.execute(text(f"ALTER TABLE items ADD COLUMN {name} {sql_type}"))


def get_session():
    with SessionLocal() as session:
        yield session
