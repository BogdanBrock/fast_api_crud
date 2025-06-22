"""Модуль для создания утилит."""


def check_json_data(response, expected_data):
    """Функция для проверки полей и значений для json-формата."""
    response_data = response.json()
    request_method = response.request.method
    missing_keys = expected_data.keys() - response_data.keys()
    assert not missing_keys, (
        f'Проверьте, что {request_method}-запрос содержит в теле '
        f'ответа такие поля как: `{"`, `".join(missing_keys)}`'
    )
    wrong_data = [
        k for k in expected_data if expected_data[k] != response_data[k]
    ]
    assert not wrong_data, (
        f'Проверьте, что {request_method}-запрос содержит правильные данные '
        f'в таких полях как: `{"`, `".join(wrong_data)}`'
    )


def check_db_data(response, expected_data, obj):
    """Функция для проверки значений в полях БД."""
    request_method = response.request.method
    db_data = {key: getattr(obj, key) for key in expected_data}
    wrong_data = {k for k in expected_data if expected_data[k] != db_data[k]}
    assert not wrong_data, (
        f'Проверьте, что при {request_method}-запросе содержатся правильные '
        f'данные в БД в таких полях как: `{"`, `".join(wrong_data)}`'
    )


def check_db_fields(db_fields, model_class):
    """Функция для проверки наличия полей в БД."""
    expected_fields = set(db_fields)
    db_keys = {key for key in expected_fields if hasattr(model_class, key)}
    missing_keys = expected_fields - db_keys
    assert not missing_keys, (
        f'Проверьте, что модель {model_class.__name__} '
        f'содержит такие поля как: `{"`, `".join(missing_keys)}`'
    )


async def create_db_obj(test_db_session, model_obj):
    """Функция для создания объекта модели."""
    test_db_session.add(model_obj)
    await test_db_session.commit()
    await test_db_session.refresh(model_obj)
    return model_obj
