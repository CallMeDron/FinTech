from pydantic import BaseModel, StringConstraints, Field, EmailStr, model_validator
from typing import Annotated, Optional
from datetime import datetime, date


class Product(BaseModel):
    name_and_version: Annotated[str, StringConstraints(min_length=3, max_length=50)]
    product_code: Annotated[str, StringConstraints(min_length=3, max_length=50)]
    min_load_term: Annotated[int, Field(gt=0, lt=121)]
    max_load_term: Annotated[int, Field(gt=0, lt=121)]
    min_principal_amount: Annotated[int, Field(gt=0)]
    max_principal_amount: Annotated[int, Field(gt=0)]
    min_interest: Annotated[float, Field(gt=0.0, lt=100.0)]
    max_interest: Annotated[float, Field(gt=0.0, lt=100.0)]
    min_origination_amount: Annotated[int, Field(gt=0)]
    max_origination_amount: Annotated[int, Field(gt=0)]

    @model_validator(mode='after')
    def validate(self):
        if (self.max_load_term < self.min_load_term or
                self.max_principal_amount < self.min_principal_amount or
                self.max_interest < self.min_interest or
                self.max_origination_amount < self.min_origination_amount):
            raise ValueError('max must be greater then min')
        return self

    class Config:
        from_attributes = True


class Agreement(BaseModel):
    client_id: int
    product_id: int
    load_term: Annotated[int, Field(gt=0, lt=121)]
    principal_amount: Annotated[int, Field(gt=0)]
    interest: Annotated[float, Field(gt=0.0, lt=100.0)]
    origination_amount: Annotated[int, Field(gt=0)]
    activation_dttm: datetime
    agreement_status: Annotated[str, StringConstraints(min_length=3, max_length=50)]

    @model_validator(mode='after')
    def validate(self):
        if self.activation_dttm < date(2000, 1, 1):
            raise ValueError('activation date must be greater then 2000-01-01')
        return self

    class Config:
        from_attributes = True


class Client(BaseModel):
    name: Annotated[str, StringConstraints(min_length=2, max_length=50)]
    surname: Annotated[str, StringConstraints(min_length=2, max_length=50)]
    patronymic: Optional[Annotated[str, StringConstraints(min_length=2, max_length=50)]]
    birthday: date
    phone: Annotated[str, StringConstraints(min_length=5, max_length=50)]
    email: EmailStr
    passport: Annotated[str, StringConstraints(min_length=10, max_length=50)]
    monthly_income: Annotated[int, Field(gt=0)]

    @model_validator(mode='after')
    def validate(self):
        if not date(1900, 1, 1) < self.birthday < date(2006, 1, 1):
            raise ValueError('birthday must be between 1900-01-01 and 2006-01-01')
        return self

    class Config:
        from_attributes = True


class PaymentSchedule(BaseModel):
    agreement_id: int
    schedule_iteration: Annotated[int, Field(gt=1)]
    payment_date: date
    period_start: date
    period_end: date
    body_payment_amount: Annotated[float, Field(gt=0.0)]
    interest_payment_amount: Annotated[float, Field(gt=0.0)]
    payment_number: Annotated[int, Field(gt=1)]
    payment_status: Annotated[str, StringConstraints(min_length=2, max_length=50)]

    @model_validator(mode='after')
    def validate(self):
        if (self.period_end < self.period_start or
                self.payment_date < date(2000, 1, 1) or
                self.period_start < date(2000, 1, 1) or
                self.period_end < date(2000, 1, 1)):
            raise ValueError('end must be greater then start and all dates must be greater then 2000-01-01')
        return self

    class Config:
        from_attributes = True


class SiteForm(BaseModel):
    product_code: Annotated[str, StringConstraints(min_length=3, max_length=50)]
    first_name: Annotated[str, StringConstraints(min_length=2, max_length=50)]
    second_name: Annotated[str, StringConstraints(min_length=2, max_length=50)]
    third_name: Annotated[Optional[str], StringConstraints(min_length=2, max_length=50)]
    birthday: date
    passport_number: Annotated[str, StringConstraints(min_length=10, max_length=50)]
    email: EmailStr
    phone: Annotated[str, StringConstraints(min_length=5, max_length=50)]
    salary: Annotated[int, Field(gt=0)]
    term: Annotated[int, Field(gt=0, lt=121)]
    interest: Annotated[float, Field(gt=0.0, lt=100.0)]
    disbursment_amount: Annotated[int, Field(gt=0)]

    @model_validator(mode='after')
    def validate(self):
        if not date(1900, 1, 1) < self.birthday < date(2006, 1, 1):
            raise ValueError('birthday must be between 1900-01-01 and 2006-01-01')
        return self

    class Config:
        from_attributes = True


class InvalidDataMessage(BaseModel):
    message: str


class AgreementID(BaseModel):
    agreement_id: int
