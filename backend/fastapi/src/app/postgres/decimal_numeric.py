from decimal import Decimal
from typing import Self

from sqlalchemy import Numeric, TypeDecorator


class DecimalNumeric(TypeDecorator[Decimal]):
    """Конвертирует Numeric PostgreSQL в Decimal python и обратно."""

    impl = Numeric
    cache_ok = True

    def process_bind_param(
        self: Self,
        value: Decimal | None,
        dialect,
    ) -> str | None:
        """Обработка значения перед отправкой в базу данных.

        Parameters
        ----------
        value: Decimal | None
            Десятичное значение для отправки в базу данных.
        dialect: Dialect
            Диалект базы данных.

        Returns
        -------
        Decimal | None
            Десятичное представление значения, если оно не равно None, иначе None.

        """
        if value is not None:
            return str(value)
        return value

    def process_result_value(
        self: Self,
        value: str | None,
        dialect,
    ) -> Decimal | None:
        """Обработка значения после получения из базы данных.

        Parameters
        ----------
        value: Decimal | None
            Десятичное значение, полученное из базы данных.
        dialect: Dialect
            Диалект базы данных.

        Returns
        -------
        Decimal | None
            Десятичное представление значения, если оно не равно None, иначе None.

        """
        if value is not None:
            return Decimal(value)
        return value
