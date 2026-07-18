# app/models/models.py
import enum
from datetime import datetime, time, date as date_
from typing import Optional, List, Dict

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, ForeignKey, BigInteger,
    Text, DateTime, Date, Enum, CheckConstraint, Index, UniqueConstraint, JSON, text
)
from sqlalchemy.orm import relationship, declarative_base, Mapped, mapped_column
from sqlalchemy.sql import func

Base = declarative_base()

# --- Enums ---
class UserRole(str, enum.Enum):
    CLIENT = "client"
    MODEL = "model"
    MASTER = "master"
    BUSINESS = "business"
    ADMIN = "admin"

class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class SubscriptionTier(str, enum.Enum):
    START = "start"
    PRO = "pro"
    PREMIUM = "premium"

class SalonRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    # MASTER сюда сознательно не входит: у мастера уже есть своя таблица
    # Master с operatonal-доступом, заскоупленным через Master.user_id —
    # ему не нужен настраиваемый словарь прав, который тут нужен owner/admin.

class InventoryMovementType(str, enum.Enum):
    RECEIPT = "receipt"          # приход (закупка)
    CONSUMPTION = "consumption"  # списание по факту после клиента
    ADJUSTMENT = "adjustment"    # корректировка по итогам инвентаризации

class InventoryAuditStatus(str, enum.Enum):
    DRAFT = "draft"          # акт открыт, идёт пересчёт
    CONFIRMED = "confirmed"  # акт закрыт, остатки скорректированы

class LoyaltyStatusSource(str, enum.Enum):
    AUTO = "auto"      # статус выставлен автоматически по числу визитов
    MANUAL = "manual"  # статус выставлен/снят вручную админом

class LoyaltyPointsMovementType(str, enum.Enum):
    ACCRUAL = "accrual"            # автоначисление % от чека после оплаты
    MANUAL_ADD = "manual_add"      # ручное начисление админом
    REDEEMED = "redeemed"          # списание баллов клиентом при оплате
    MANUAL_REMOVE = "manual_remove"  # ручное списание админом (коррекция)

# Ключи прав салона. Значение — можно ли делать соответствующее действие.
# У создателя салона (SalonMember.is_creator=True) все права всегда True
# независимо от словаря, плюс только он может удалить сам салон.
SALON_PERMISSION_KEYS = (
    "manage_salon",      # настройки, фото, описание, график салона
    "manage_owners",     # приглашать/снимать совладельцев, менять их права
    "manage_admins",     # приглашать/снимать админов
    "manage_masters",    # CRUD мастеров, услуг, графика мастера
    "manage_schedule",   # быстрые записи, отметка выполнено/неявка
    "manage_promotions",
    "manage_reviews",    # ответы на отзывы
    "view_finances",
    "manage_tariff",
    "view_audit_log",
    "manage_inventory",  # склад мастеров: приход, списания, инвентаризация
    "manage_payroll",    # ставки мастеров, ручные бонусы/штрафы
)

OWNER_DEFAULT_PERMISSIONS: Dict[str, bool] = {k: True for k in SALON_PERMISSION_KEYS}
ADMIN_DEFAULT_PERMISSIONS: Dict[str, bool] = {
    **OWNER_DEFAULT_PERMISSIONS,
    "view_finances": False,
    "manage_tariff": False,
    "manage_owners": False,
    "view_audit_log": False,
    "manage_inventory": False,
    "manage_payroll": False,
}

# --- Core Tables ---

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    phone: Mapped[str] = mapped_column(String(15), unique=True, index=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True, nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.CLIENT, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Привязка Telegram для уведомлений (блок 18+): chat_id из бота.
    # BigInteger — телеграмовские id не влезают в int32. NULL = не привязан.
    tg_chat_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True, index=True)

    subscription_tier: Mapped[Optional[SubscriptionTier]] = mapped_column(Enum(SubscriptionTier), nullable=True)
    subscription_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    master_profile: Mapped[Optional["Master"]] = relationship(back_populates="user", uselist=False)
    created_salons: Mapped[List["Salon"]] = relationship(back_populates="creator")
    salon_memberships: Mapped[List["SalonMember"]] = relationship(back_populates="user", foreign_keys="SalonMember.user_id")
    bookings: Mapped[List["Booking"]] = relationship(back_populates="client", foreign_keys="Booking.client_id")
    reviews: Mapped[List["Review"]] = relationship(back_populates="client")
    favorites: Mapped[List["Favorite"]] = relationship(back_populates="user")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Salon(Base):
    __tablename__ = "salons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # Пользователь, создавший карточку салона. Не источник правды для прав —
    # тот источник теперь SalonMember (role=owner, is_creator=True для этого же
    # user_id). creator_id остаётся как исторический/справочный указатель и не
    # уникален: один человек может быть создателем нескольких салонов.
    creator_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    creator: Mapped["User"] = relationship(back_populates="created_salons")
    members: Mapped[List["SalonMember"]] = relationship(back_populates="salon", cascade="all, delete-orphan")
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    address: Mapped[str] = mapped_column(String(255), nullable=False)

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    photos: Mapped[List["SalonPhoto"]] = relationship(back_populates="salon")

    rating: Mapped[float] = mapped_column(Float, default=0.0)
    reviews_count: Mapped[int] = mapped_column(Integer, default=0)

    working_hours: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    business_tier: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="Europe/Moscow", server_default="Europe/Moscow", nullable=False)

    masters: Mapped[List["Master"]] = relationship(back_populates="salon")
    promotions: Mapped[List["Promotion"]] = relationship(back_populates="salon")
    reviews: Mapped[List["Review"]] = relationship(back_populates="salon")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class SalonPhoto(Base):
    __tablename__ = "salon_photos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    salon_id: Mapped[int] = mapped_column(ForeignKey("salons.id", ondelete="CASCADE"))
    url: Mapped[str] = mapped_column(String(500))
    salon: Mapped["Salon"] = relationship(back_populates="photos")

class SalonMember(Base):
    """Членство пользователя в бизнес-панели салона (owner/admin) с гибкими правами."""
    __tablename__ = "salon_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    salon_id: Mapped[int] = mapped_column(ForeignKey("salons.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    role: Mapped[SalonRole] = mapped_column(Enum(SalonRole), nullable=False)
    is_creator: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    permissions: Mapped[Dict[str, bool]] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)

    invited_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    salon: Mapped["Salon"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="salon_memberships", foreign_keys=[user_id])

    __table_args__ = (
        UniqueConstraint("salon_id", "user_id", name="uq_salon_member"),
        Index("ix_salon_members_user", "user_id"),
        Index(
            "uq_salon_creator", "salon_id", unique=True,
            postgresql_where=text("is_creator = true"),
        ),
    )

class Master(Base):
    __tablename__ = "masters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    salon_id: Mapped[int] = mapped_column(ForeignKey("salons.id"))

    specialization: Mapped[str] = mapped_column(String(100), nullable=False)
    experience_years: Mapped[int] = mapped_column(Integer, default=0)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    rating: Mapped[float] = mapped_column(Float, default=0.0)
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    break_minutes: Mapped[int] = mapped_column(Integer, default=15, server_default="15", nullable=False)
    
    user: Mapped["User"] = relationship(back_populates="master_profile")
    salon: Mapped["Salon"] = relationship(back_populates="masters")
    services: Mapped[List["Service"]] = relationship(back_populates="master")
    schedule: Mapped[List["Schedule"]] = relationship(back_populates="master")
    reviews: Mapped[List["Review"]] = relationship(back_populates="master")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    master_id: Mapped[int] = mapped_column(ForeignKey("masters.id"))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    master: Mapped["Master"] = relationship(back_populates="services")

class Schedule(Base):
    __tablename__ = "schedule"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    master_id: Mapped[int] = mapped_column(ForeignKey("masters.id"))
    day_of_week: Mapped[int] = mapped_column(Integer)
    start_time: Mapped[time] = mapped_column()
    end_time: Mapped[time] = mapped_column()

    master: Mapped["Master"] = relationship(back_populates="schedule")

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    master_id: Mapped[int] = mapped_column(ForeignKey("masters.id"))
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)

    status: Mapped[BookingStatus] = mapped_column(Enum(BookingStatus), default=BookingStatus.PENDING)
    # Скидка лояльности салона, применённая админом при завершении записи
    # (0, если не применялась). Считается и пишется в complete_booking —
    # см. app/services/loyalty_service.py.
    discount_percent: Mapped[int] = mapped_column(Integer, default=0)
    final_price: Mapped[int] = mapped_column(Integer, nullable=True)
    # Что именно применили: "regular_client" / "personal" / текст промокода / NULL.
    loyalty_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    bonus_points_redeemed: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    # Мастер отчитался о фактически потраченных расходниках по этому визиту
    # (форма склада после клиента). Флаг для напоминаний мастеру/админу —
    # сам факт списания хранится в InventoryMovement(booking_id=...).
    consumption_reported: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)

    client: Mapped["User"] = relationship(back_populates="bookings", foreign_keys=[client_id])
    master: Mapped["Master"] = relationship()
    service: Mapped["Service"] = relationship()

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_bookings_master_start', 'master_id', 'start_time'),
    )

class Promotion(Base):
    __tablename__ = "promotions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    salon_id: Mapped[int] = mapped_column(ForeignKey("salons.id"))
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    tag: Mapped[str] = mapped_column(String(30), nullable=False)

    salon: Mapped["Salon"] = relationship(back_populates="promotions")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class Review(Base):
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    master_id: Mapped[int] = mapped_column(ForeignKey("masters.id"))
    salon_id: Mapped[int] = mapped_column(ForeignKey("salons.id"))
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    client: Mapped["User"] = relationship(back_populates="reviews")
    master: Mapped["Master"] = relationship(back_populates="reviews")
    salon: Mapped["Salon"] = relationship(back_populates="reviews")

    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    )

# ========== НОВАЯ МОДЕЛЬ: Избранное ==========
class Favorite(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    salon_id: Mapped[Optional[int]] = mapped_column(ForeignKey("salons.id"), nullable=True)
    master_id: Mapped[Optional[int]] = mapped_column(ForeignKey("masters.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="favorites")
    salon: Mapped[Optional["Salon"]] = relationship()
    master: Mapped[Optional["Master"]] = relationship()

    __table_args__ = (
        # Один салон/мастер — один раз в избранном пользователя. Частичные
        # уникальные индексы (salon_id/master_id взаимоисключающе NULL);
        # страховка от гонки двух параллельных toggle-запросов.
        Index(
            "uq_favorite_user_salon", "user_id", "salon_id", unique=True,
            postgresql_where=text("salon_id IS NOT NULL"),
        ),
        Index(
            "uq_favorite_user_master", "user_id", "master_id", unique=True,
            postgresql_where=text("master_id IS NOT NULL"),
        ),
    )

# ========== Аудит действий администратора ==========
class AdminAudit(Base):
    __tablename__ = "admin_audit"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id"))   # кто совершил действие
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # change_role, toggle_active, delete_user, …
    target_type: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)  # user / salon / review
    target_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # человекочитаемое описание
    # NULL = платформенное действие (суперадмин). Заполнено — действие внутри
    # конкретного салона (приглашение/снятие сотрудника, удаление салона и т.п.).
    # ondelete=SET NULL: при удалении салона лог остаётся, просто теряет привязку.
    salon_id: Mapped[Optional[int]] = mapped_column(ForeignKey("salons.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    actor: Mapped["User"] = relationship()

    __table_args__ = (
        Index("ix_admin_audit_created", "created_at"),
        Index("ix_admin_audit_salon", "salon_id"),
    )

# ========== Склад расходников (мини-склад на каждого мастера) ==========
class InventoryItem(Base):
    """Позиция номенклатуры на мини-складе конкретного мастера."""
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    master_id: Mapped[int] = mapped_column(ForeignKey("masters.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)  # мл / г / шт / уп
    # Текущий остаток — денормализованная сумма всех InventoryMovement.delta
    # по этой позиции; движения остаются источником истины и историей.
    quantity: Mapped[float] = mapped_column(Float, default=0.0, server_default="0", nullable=False)
    cost_per_unit: Mapped[int] = mapped_column(Integer, nullable=False)  # для себестоимости
    min_quantity: Mapped[float] = mapped_column(Float, default=0.0, server_default="0", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    master: Mapped["Master"] = relationship()

class InventoryMovement(Base):
    """Журнал движений по складу — единый источник истины для остатка и COGS."""
    __tablename__ = "inventory_movements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("inventory_items.id", ondelete="CASCADE"))
    type: Mapped[InventoryMovementType] = mapped_column(Enum(InventoryMovementType), nullable=False)
    delta: Mapped[float] = mapped_column(Float, nullable=False)  # знак = направление движения
    # Цена за единицу на момент движения — чтобы себестоимость прошлых
    # периодов не «плыла» при изменении текущей цены позиции.
    unit_cost_snapshot: Mapped[int] = mapped_column(Integer, nullable=False)
    booking_id: Mapped[Optional[int]] = mapped_column(ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    item: Mapped["InventoryItem"] = relationship()
    booking: Mapped[Optional["Booking"]] = relationship()
    created_by: Mapped["User"] = relationship()

    __table_args__ = (
        Index("ix_inventory_movements_item", "item_id"),
        Index("ix_inventory_movements_booking", "booking_id"),
    )

class InventoryAudit(Base):
    """Акт инвентаризации мини-склада мастера."""
    __tablename__ = "inventory_audits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    master_id: Mapped[int] = mapped_column(ForeignKey("masters.id", ondelete="CASCADE"))
    status: Mapped[InventoryAuditStatus] = mapped_column(
        Enum(InventoryAuditStatus), default=InventoryAuditStatus.DRAFT, nullable=False
    )
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    master: Mapped["Master"] = relationship()
    created_by: Mapped["User"] = relationship()
    items: Mapped[List["InventoryAuditItem"]] = relationship(back_populates="audit", cascade="all, delete-orphan")

class InventoryAuditItem(Base):
    """Строка акта: системный остаток на старте пересчёта vs фактический."""
    __tablename__ = "inventory_audit_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    audit_id: Mapped[int] = mapped_column(ForeignKey("inventory_audits.id", ondelete="CASCADE"))
    item_id: Mapped[int] = mapped_column(ForeignKey("inventory_items.id", ondelete="CASCADE"))
    expected_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    actual_quantity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    audit: Mapped["InventoryAudit"] = relationship(back_populates="items")
    item: Mapped["InventoryItem"] = relationship()

# ========== Зарплаты: ставка мастера + ручные бонусы/штрафы ==========
class MasterPayrollSettings(Base):
    """Ставка мастера: оклад за период + % от выручки. 1–1 с Master."""
    __tablename__ = "master_payroll_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    master_id: Mapped[int] = mapped_column(ForeignKey("masters.id", ondelete="CASCADE"), unique=True)
    base_salary: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    commission_percent: Mapped[float] = mapped_column(Float, default=0.0, server_default="0", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    master: Mapped["Master"] = relationship()

class PayrollAdjustment(Base):
    """Ручное начисление админом: бонус (amount > 0) или штраф (amount < 0)."""
    __tablename__ = "payroll_adjustments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    master_id: Mapped[int] = mapped_column(ForeignKey("masters.id", ondelete="CASCADE"))
    period_month: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)  # 1-е число месяца
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    master: Mapped["Master"] = relationship()
    created_by: Mapped["User"] = relationship()

    __table_args__ = (
        Index("ix_payroll_adjustments_master_period", "master_id", "period_month"),
    )

# ========== Promo-модели салона (роль UserRole.MODEL, отдельно от мастеров) ==========
class SalonModel(Base):
    """Привязка пользователя с ролью MODEL к салону (кастинг/сотрудничество для контента)."""
    __tablename__ = "salon_models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    salon_id: Mapped[int] = mapped_column(ForeignKey("salons.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    stage_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    salon: Mapped["Salon"] = relationship()
    user: Mapped["User"] = relationship()

    __table_args__ = (
        UniqueConstraint("salon_id", "user_id", name="uq_salon_model"),
    )

# ========== Заметки на карточке клиента ==========
class ClientNote(Base):
    """Заметка владельца/админа салона на карточке клиента."""
    __tablename__ = "client_notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    salon_id: Mapped[int] = mapped_column(ForeignKey("salons.id", ondelete="CASCADE"))
    client_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    salon: Mapped["Salon"] = relationship()
    client: Mapped["User"] = relationship(foreign_keys=[client_id])
    author: Mapped["User"] = relationship(foreign_keys=[author_id])

    __table_args__ = (
        Index("ix_client_notes_salon_client", "salon_id", "client_id"),
    )

# ========== Лояльность салона: статус, персональные скидки, бонусы ==========
class SalonLoyaltySettings(Base):
    """Настройки программы лояльности салона (1–1 с Salon)."""
    __tablename__ = "salon_loyalty_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    salon_id: Mapped[int] = mapped_column(ForeignKey("salons.id", ondelete="CASCADE"), unique=True)
    regular_client_discount_percent: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    # Автоприсвоение статуса «постоянный клиент» после N визитов за 12 мес.
    # NULL = только вручную админом.
    regular_client_visits_threshold: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    # % от final_price, автоматически зачисляемый баллами после оплаты. 0 = выключено.
    bonus_accrual_percent: Mapped[float] = mapped_column(Float, default=0.0, server_default="0", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    salon: Mapped["Salon"] = relationship()

class LoyaltyOffer(Base):
    """Именная скидка/промокод, который салон создаёт сам («позиция»)."""
    __tablename__ = "loyalty_offers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    salon_id: Mapped[int] = mapped_column(ForeignKey("salons.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    discount_percent: Mapped[int] = mapped_column(Integer, nullable=False)
    promo_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    salon: Mapped["Salon"] = relationship()

    __table_args__ = (
        UniqueConstraint("salon_id", "promo_code", name="uq_loyalty_offer_promo_code"),
    )

class ClientLoyalty(Base):
    """Состояние лояльности клиента в конкретном салоне."""
    __tablename__ = "client_loyalty"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    salon_id: Mapped[int] = mapped_column(ForeignKey("salons.id", ondelete="CASCADE"))
    client_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    is_regular_client: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    regular_client_source: Mapped[Optional[LoyaltyStatusSource]] = mapped_column(Enum(LoyaltyStatusSource), nullable=True)
    # Персональная скидка этому конкретному клиенту, отдельно от статуса «постоянный клиент».
    personal_discount_percent: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bonus_points: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    salon: Mapped["Salon"] = relationship()
    client: Mapped["User"] = relationship()

    __table_args__ = (
        UniqueConstraint("salon_id", "client_id", name="uq_client_loyalty"),
    )

class LoyaltyPointsMovement(Base):
    """Журнал изменений бонусного баланса клиента (начисление/списание)."""
    __tablename__ = "loyalty_points_movements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_loyalty_id: Mapped[int] = mapped_column(ForeignKey("client_loyalty.id", ondelete="CASCADE"))
    type: Mapped[LoyaltyPointsMovementType] = mapped_column(Enum(LoyaltyPointsMovementType), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # знак = направление
    booking_id: Mapped[Optional[int]] = mapped_column(ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    client_loyalty: Mapped["ClientLoyalty"] = relationship()
    booking: Mapped[Optional["Booking"]] = relationship()
    created_by: Mapped["User"] = relationship()

    __table_args__ = (
        Index("ix_loyalty_points_movements_client_loyalty", "client_loyalty_id"),
    )

# ========== Закрытые даты (весь салон или конкретный мастер) ==========
class ScheduleClosure(Base):
    """Дата, закрытая для записи — на весь салон (master_id=NULL) либо на
    одного мастера (отпуск/больничный). Отдельно от Salon.working_hours,
    который описывает только повторяющийся по дням недели график."""
    __tablename__ = "schedule_closures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    salon_id: Mapped[int] = mapped_column(ForeignKey("salons.id", ondelete="CASCADE"))
    master_id: Mapped[Optional[int]] = mapped_column(ForeignKey("masters.id", ondelete="CASCADE"), nullable=True)
    date: Mapped[date_] = mapped_column(Date, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    salon: Mapped["Salon"] = relationship()
    master: Mapped[Optional["Master"]] = relationship()
    created_by: Mapped["User"] = relationship()

    __table_args__ = (
        # Одно закрытие "всего салона" на дату
        Index(
            "uq_schedule_closure_salon", "salon_id", "date", unique=True,
            postgresql_where=text("master_id IS NULL"),
        ),
        # Одно закрытие конкретного мастера на дату
        Index(
            "uq_schedule_closure_master", "salon_id", "master_id", "date", unique=True,
            postgresql_where=text("master_id IS NOT NULL"),
        ),
    )
