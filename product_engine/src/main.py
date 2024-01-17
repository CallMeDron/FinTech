from fastapi import FastAPI, Depends
from fastapi.openapi.utils import get_openapi
from fastapi.responses import Response, JSONResponse
from fastapi.exceptions import RequestValidationError

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from typing import Optional
from random import randint
from datetime import datetime

from database import create_db_session
from dao_models_repository import Repository
import pydantic_models

app = FastAPI()

EMPTY = {"content": {"None": {"example": ""}}}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc) -> JSONResponse | Response:
    """
    Кастомный обработчик исключений по валидации.
    При ошибке валидации хочу возвращать код 400 вместо 422.
    Согласно тз тело ответа может быть пустым или JSON'кой в зависимости от запроса
    """
    if str(request.url).split('/')[-1] == "agreement":
        location: str = exc.errors()[0]['loc'][-1]
        content: pydantic_models.InvalidDataMessage = \
            {'message': f"{(location + ':') if location != 'body' else ''} {exc.errors()[0]['msg']}"}
        return JSONResponse(content, status_code=400)

    return Response(status_code=400)


def custom_openapi() -> dict[str, any]:
    """
    Перегрузка функции app.openapi, чтобы удалить из сваггера код 422 (который я не возвращаю)
    и соответствующие схемы pydantic (HTTPValidationError и ValidationError)
    https://fastapi.tiangolo.com/how-to/extending-openapi/#generate-the-openapi-schema
    https://github.com/tiangolo/fastapi/issues/3424?ysclid=lr0jismi42241528005#issuecomment-1283484665
    """
    if not app.openapi_schema:
        app.openapi_schema = get_openapi(title="FastAPI", version="0.1.0", routes=app.routes)

    for _, method_item in app.openapi_schema.get('paths').items():
        for _, param in method_item.items():
            responses = param.get('responses')
            if '422' in responses:
                del responses['422']

    for schema in ('HTTPValidationError', 'ValidationError'):
        if schema in app.openapi_schema['components']['schemas']:
            del app.openapi_schema['components']['schemas'][schema]

    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/product/{product_code}", response_model=pydantic_models.Product, responses={404: EMPTY})
async def get_product_by_code(product_code: str,
                              db_session: Session = Depends(create_db_session)) -> Repository.Product | Response:
    """
    Возвращает продукт по короткому коду, если он существует в базе
    """
    product = await Repository.get_one(db_session, Repository.Product, {'product_code': product_code})
    return product if product else Response(status_code=404)


@app.get("/product", response_model=list[pydantic_models.Product])
async def get_all_products(db_session: Session = Depends(create_db_session)) -> list[Repository.Product]:
    """
    Возвращает список существующих продуктов
    """
    return await Repository.get_all(db_session, Repository.Product)


@app.post("/product", response_class=Response, responses={200: EMPTY, 400: EMPTY, 409: EMPTY})
async def create_product(product: pydantic_models.Product,
                         db_session: Session = Depends(create_db_session)) -> Response:
    """
    Создаёт новый продукт, загружает его в базу
    """
    db_product = await Repository.get_one(db_session, Repository.Product, {'product_code': product.product_code})

    if db_product:
        return Response(status_code=409)
    try:
        await Repository.create(db_session, Repository.Product, product.model_dump())
    except IntegrityError:
        return Response(status_code=409)

    return Response()


@app.delete("/product/{product_code}", response_class=Response, responses={200: EMPTY})
async def delete_product_by_code(product_code: str, db_session: Session = Depends(create_db_session)) -> Response:
    """
    Удаляет продукт по короткому коду
    """
    await Repository.delete(db_session, Repository.Product, {'product_code': product_code})
    return Response()


@app.post("/agreement", responses={200: {"model": pydantic_models.AgreementID},
                                   400: {"model": pydantic_models.InvalidDataMessage}})
async def create_agreement(site_form: pydantic_models.SiteForm,
                           db_session: Session = Depends(create_db_session)) -> JSONResponse:
    """
    Создание заявки на кредит по форме с сайта
    """
    conditions = {'passport': site_form.passport_number,
                  'name': site_form.first_name,
                  'surname': site_form.second_name,
                  'patronymic': site_form.third_name,
                  'birthday': site_form.birthday,
                  'phone': site_form.phone,
                  'email': site_form.email,
                  'monthly_income': site_form.salary}

    client: Optional[Repository.Client] = await Repository.get_one(db_session, Repository.Client, conditions)

    if client:
        client_id = client.client_id
    else:
        '''
        Клиента с точным совпадением всех полей может не быть, но уникальные поля (паспорт, номер, почта)
        уже могут быть заняты, что вызовет ошибку при попытке создать запись в таблице
        '''
        try:
            client: Repository.Client = await Repository.create(db_session, Repository.Client, conditions)
        except IntegrityError:
            return JSONResponse({'message': 'Пользователь с таким паспортом/телефоном/почтой уже существует'},
                                status_code=400)
        client_id = client.client_id

    product: Optional[Repository.Product] = \
        await Repository.get_one(db_session, Repository.Product, {'product_code': site_form.product_code})

    if product:
        origination_amount = randint(product.min_origination_amount, product.max_origination_amount)
        principal_amount = site_form.disbursment_amount + origination_amount

        for left, x, right, field in ((product.min_load_term, site_form.term, product.max_load_term, 'term'),
                                      (product.min_interest, site_form.interest, product.max_interest, 'interest'),
                                      (product.min_principal_amount, principal_amount, product.max_principal_amount,
                                       'principal amount')):
            if not left <= x <= right:
                message = f'{field} = {x}, must be in [{left}, {right}]'
                return JSONResponse({'message': message}, status_code=400)

    else:
        return JSONResponse({'message': f"no product with code '{site_form.product_code}'"}, status_code=400)

    conditions = {'client_id': client_id,
                  'product_id': product.product_id,
                  'load_term': site_form.term,
                  'principal_amount': principal_amount,
                  'interest': site_form.interest,
                  'origination_amount': origination_amount,
                  'activation_dttm': datetime.now(),
                  'agreement_status': 'New'}

    agreement: Repository.Agreement = await Repository.create(db_session, Repository.Agreement, conditions)

    return JSONResponse(content={'agreement_id': agreement.agreement_id})
