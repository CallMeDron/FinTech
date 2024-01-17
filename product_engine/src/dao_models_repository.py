from sqlalchemy import Column, ForeignKey, Integer, String, Float, TIMESTAMP, DATE, select, Select
from sqlalchemy.orm import relationship, Session

from typing import Any, Optional, TypeVar

from database import Base, engine

T = TypeVar('T', bound=Base)


class Repository:
    class Product(Base):
        __tablename__ = "product"

        product_id = Column(Integer, primary_key=True)
        name_and_version = Column(String(50), nullable=False, unique=True, index=True)
        product_code = Column(String(50), nullable=False, unique=True, index=True)
        min_load_term = Column(Integer, nullable=False)
        max_load_term = Column(Integer, nullable=False)
        min_principal_amount = Column(Integer, nullable=False)
        max_principal_amount = Column(Integer, nullable=False)
        min_interest = Column(Float, nullable=False)
        max_interest = Column(Float, nullable=False)
        min_origination_amount = Column(Integer, nullable=False)
        max_origination_amount = Column(Integer, nullable=False)

    class Agreement(Base):
        __tablename__ = "agreement"

        agreement_id = Column(Integer, primary_key=True)
        client_id = Column(Integer, ForeignKey("client.client_id"), nullable=False, index=True)
        product_id = Column(Integer, ForeignKey("product.product_id"), nullable=False, index=True)
        load_term = Column(Integer, nullable=False)
        principal_amount = Column(Integer, nullable=False)
        interest = Column(Float, nullable=False)
        origination_amount = Column(Integer, nullable=False)
        activation_dttm = Column(TIMESTAMP, nullable=False, index=True)
        agreement_status = Column(String(50), nullable=False, index=True)

        client = relationship("Client")
        product = relationship("Product")

    class Client(Base):
        __tablename__ = "client"

        client_id = Column(Integer, primary_key=True)
        name = Column(String(50), nullable=False)
        surname = Column(String(50), nullable=False)
        patronymic = Column(String(50))
        birthday = Column(DATE, nullable=False)
        phone = Column(String(50), nullable=False, index=True)
        email = Column(String(50), nullable=False)
        passport = Column(String(50), nullable=False, index=True)
        monthly_income = Column(Integer, nullable=False)

    class PaymentSchedule(Base):
        __tablename__ = "payment_schedule"

        schedule_id = Column(Integer, primary_key=True)
        agreement_id = Column(Integer, ForeignKey("agreement.agreement_id"), nullable=False, index=True)
        schedule_iteration = Column(Integer, nullable=False, index=True)
        payment_date = Column(DATE, nullable=False, index=True)
        period_start = Column(DATE, nullable=False)
        period_end = Column(DATE, nullable=False)
        body_payment_amount = Column(Float, nullable=False)
        interest_payment_amount = Column(Float, nullable=False)
        payment_number = Column(Integer, nullable=False)
        payment_status = Column(String(50), nullable=False, index=True)

        agreement = relationship("Agreement")

    Base.metadata.create_all(bind=engine)

    @staticmethod
    async def get_one(db_session: Session, model: T, conditions: dict[str, Any]) -> Optional[T]:
        """
        Возвращает единственный экземпляр модели из БД по условию
        :param db_session: сессия БД
        :param model: ДАО модель
        :param conditions: условия выбора
        :return: экземпляр модели или None
        """
        statement: Select = select(model).filter_by(**conditions)
        return db_session.execute(statement).scalar()

    @staticmethod
    async def get_all(db_session: Session, model: T) -> list[T]:
        """
        Вовращает список всех экземпляров модели из БД
        :param db_session: сессия БД
        :param model: ДАО модель
        :return: список экземпляров модели
        """
        statement: Select = select(model)
        return db_session.execute(statement).scalars().all()

    @staticmethod
    async def create(db_session: Session, model: T, fields: dict[str, Any]) -> T:
        """
        Добавляет в БД экземпляр модели с заданными полями
        :param db_session: сессия БД
        :param model: ДАО модель
        :param fields: значения полей модели
        :return: созданный и обновлённый экземпляр модели
        """
        db_object: T = model(**fields)
        db_session.add(db_object)
        db_session.commit()
        db_session.refresh(db_object)

        return db_object

    @staticmethod
    async def delete(db_session: Session, model: T, conditions: dict[str, Any]) -> None:
        """
        Удаляет из БД экземпляр модели по заданным условиям
        :param db_session: сессия БД
        :param model: ДАО модель
        :param conditions: условия выбора
        """
        db_object: Optional[T] = await Repository.get_one(db_session, model, conditions)

        if db_object:
            db_session.delete(db_object)
            db_session.commit()
