Project product_engine {
  database_type: 'PostgreSQL'
  Note: '''Сервис Product Engine (PE) отвечает за хранение 
  всех банковских продуктов вместе c их 
  условиями/характеристиками. B нашей реализации PE будет 
  отвечать также за хранение информации по клиентам, 
  их кредитах, статусах и графиках платежей.'''
}

Table product_engine.product {
  product_id integer [not null, unique, primary key, increment, note: 'Уникальный ключ продукта и версии'] 
  name_and_version varchar [not null, unique, note: 'Полное название и версия продукта']
  product_code varchar [not null, unique, note: 'Короткое внутреннее название и версия продукта']
  min_load_term integer [not null, note: 'Минимальный срок кредита, мес']
  max_load_term integer [not null, note: 'Максимальный срок кредита, мес']
  min_principal_amount integer [not null, note: 'Минимальная сумма кредита']
  max_principal_amount integer [not null, note: 'Максимальная сумма кредита']
  min_interest float [not null, note: 'Минимальная процентная ставка']
  max_interest float [not null, note: 'Максимальная процентная ставка']
  min_origination_amount integer [not null, note: 'Минимальная сумма комиссий']
  max_origination_amount integer [not null, note: 'Максимальная сумма комиссий']
  indexes {
    product_id [unique, pk]
    (name_and_version, product_code) [unique]
  }
  Note: 'Данные o продуктах'
}

Table product_engine.agreement {
  agreement_id integer [not null, unique, primary key, increment, note: 'Уникальный ключ договора']
  client_id integer [not null, note: 'Ключ клиента']
  product_id integer [not null, note: 'Ключ продукта']
  load_term integer [not null, note: 'Срок кредита, мес']
  principal_amount integer [not null, note: 'Сумма кредита']
  interest float [not null, note: 'Процентная ставка']
  origination_amount integer [not null, note: 'Сумма комиссий']
  activation_dttm timestamp [not null, note: 'Время активации договора']
  agreement_status varchar [not null, note: 'Статус договора']
  indexes {
    agreement_id [unique, pk]
    client_id
    product_id
    activation_dttm
    agreement_status
  }
  Note: 'Данные o договорах'
}

Table product_engine.client {
  client_id integer [not null, unique, primary key, increment, note: 'Уникальный ключ клиента']
  name varchar [not null, note: 'Имя клиента']
  surname varchar [not null, note: 'Фамилия клиента']
  patronymic varchar [note: 'Отчество клиента']
  birthday date [not null, note: 'Дата рождения клиента']
  phone char [not null, unique, note: 'Номер телефона клиента']
  passport char [not null, unique, note: 'Паспорт клиента']
  email char [not null, unique, note: 'Электронная почта клиента']
  monthly_income integer [not null, note: 'Ежемесячный доход клиента']
  indexes {
    client_id [unique, pk]
    phone [unique]
    passport [unique]
  }
  Note: 'Данные o клиентах'
}

Table product_engine.payment_schedule {
  schedule_id integer [not null, unique, primary key, increment, note: 'Уникальный ключ графика платежей']
  agreement_id integer [not null, note: 'Уникальный ключ договора']
  schedule_iteration integer [not null, note: 'Итерация расписания (меняется при перерасчёте)']
  payment_date date [not null, note: 'Планируемая дата платежа']
  period_start date [not null, note: 'Начало оплачиваемого периода']
  period_end date [not null, note: 'Конец оплачиваемого периода']
  body_payment_amount integer [not null, note: 'Сумма выплаты по телу долга']
  interest_payment_amount integer [not null, note: 'Сумма выплаты по процентам долга']
  payment_number integer [not null, note: 'Порядковый номер платежа']
  payment_status varchar [not null, note: 'Статус договора']
  indexes {
    schedule_id [unique, pk]
    schedule_iteration
    agreement_id
    payment_date
    payment_status
  }
  Note: 'Данные o графиках платежей'
}

Ref: product_engine.product.product_id < product_engine.agreement.product_id
Ref: product_engine.agreement.client_id > product_engine.client.client_id
Ref: product_engine.agreement.agreement_id < product_engine.payment_schedule.agreement_id