class HTTPError(Exception):
    def __init__(self, mes: str) -> None:
        self.mes = mes

    def __str__(self) -> str:
        return self.mes


class QIWIAPIError(Exception):
    def __init__(self, mes: str) -> None:
        self.mes = mes

    def __str__(self) -> str:
        return self.mes


class ArgumentError(Exception):
    def __init__(self, mes: str) -> None:
        self.mes = mes

    def __str__(self) -> str:
        return self.mes


class PriceError(Exception):
    def __init__(self, comment: str, need: int, paid: int, mes: str | None = None) -> None:
        self.comment = comment

        self.need = need
        self.paid = paid
        self.remained = need - paid

        self.mes = mes

    def __str__(self) -> str:
        return self.mes


class ExceptionFactory:
    def __init__(self, exc_lang: str = 'ru') -> None:
        self.exc_lang = exc_lang

    def arg_error(self) -> ArgumentError:  # todo rus lang
        en_msg = 'Echo function must have one argument!'
        ru_msg = 'Echo function must have one argument!'

        if self.exc_lang.lower() == 'ru':
            return ArgumentError(ru_msg)

        else:
            return ArgumentError(en_msg)

    def http_error(self, code: int) -> HTTPError:
        if code == 400:
            en_msg = 'Query syntax error (incorrect data format)'
            ru_msg = 'Ошибка синтаксиса запроса (неправильный формат данных)'

        elif code == 401:
            en_msg = 'Invalid token or API token expired'
            ru_msg = 'Неверный токен или истек срок действия токена API'

        elif code == 403:
            en_msg = 'No rights to this request (API token doesn\'t have enough permissions)'
            ru_msg = 'Нет прав на этот запрос (недостаточно разрешений у токена API)'

        elif code == 404:
            en_msg = 'Not found transaction/wallet/active webhook/account'
            ru_msg = 'Не найдено транзакция/кошелек/активный вебхук/счет'

        elif code == 422:
            en_msg = 'The domain/subnet/host of the web hook is incorrectly specified ' \
                     '(the hook type or transaction type is incorrectly specified in the param parameter for the URL ' \
                     'of the web hook, an attempt to create a hook if there is an already created one'
            ru_msg = 'Неправильно указаны домен/подсеть/хост веб-хука (в параметре param для URL веб-хука), ' \
                     'неправильно указаны тип хука или тип транзакции, попытка создать хук при наличии уже созданного'

        elif code == 423:
            en_msg = 'Too many requests, the service is temporarily unavailable'
            ru_msg = 'Слишком много запросов, сервис временно недоступен'

        elif code == 500:
            en_msg = 'Internal service error (exceeded the length of the web hook URL, infrastructure problems, ' \
                     'unavailability of any resources, etc.)'
            ru_msg = 'Внутренняя ошибка сервиса (превышена длина URL веб-хука, проблемы с инфраструктурой, ' \
                     'недоступность каких-либо ресурсов и т.д.)'

        else:
            en_msg = 'Exception, status code {}'.format(code)
            ru_msg = 'Ошибка, статус код {}'.format(code)

        if self.exc_lang.lower() == 'ru':
            return HTTPError(ru_msg)
        else:
            return HTTPError(en_msg)

    def qiwi_api_error(self, code: int) -> QIWIAPIError:  # # todo en lang
        if code == 3:
            en_msg = 'Technical error. Repeat the payment later.'
            ru_msg = 'Техническая ошибка. Повторите платеж позже.'

        elif code == 4:
            en_msg = 'Incorrect phone or invoice format. Check the data.'
            ru_msg = 'Некорректный формат телефона или счета. Проверьте данные.'

        elif code == 5:
            en_msg = ''
            ru_msg = 'Данного номера не существует. Проверьте данные и попробуйте еще раз.'

        elif code == 8:
            en_msg = ''
            ru_msg = 'Техническая проблема на стороне банка-получателя. Попробуйте позже.'

        elif code == 57:
            en_msg = ''
            ru_msg = 'Статус кошелька получателя не позволяет перевести ему деньги. Попросите владельца кошелька ' \
                     'повысить его статус: укажите паспортные данные.'

        elif code == 131:
            en_msg = ''
            ru_msg = 'Платеж недоступен для вашей страны'

        elif code == 166:
            en_msg = ''
            ru_msg = 'Ваш статус кошелька не позволяет совершить платеж. Повысьте статус кошелька: ' \
                     'укажите паспортные данные.'

        elif code == 167:
            en_msg = ''
            ru_msg = 'Статус кошелька получателя не позволяет перевести ему деньги. Попросите владельца кошелька ' \
                     'повысить его статус: указать паспортные данные.'

        elif code == 202:
            en_msg = ''
            ru_msg = 'Техническая ошибка. Повторите платеж позже.'

        elif code == 204:
            en_msg = ''
            ru_msg = 'Ваш статус кошелька не позволяет пополнять его наличными. Повысьте статус кошелька: ' \
                     'укажите паспортные данные.'

        elif code == 220:
            en_msg = ''
            ru_msg = 'Недостаточно средств. Пополните кошелек'

        elif code == 241:
            en_msg = ''
            ru_msg = 'Сумма платежа должна быть больше 1 рубля'

        elif code == 242:
            en_msg = ''
            ru_msg = 'Сумма платежа превышает максимально допустимую'

        elif code == 254:
            en_msg = ''
            ru_msg = 'Сумма платежа должна быть больше 1 рубля'

        elif code == 271:
            en_msg = ''
            ru_msg = 'Техническая проблема на стороне банка-получателя. Попробуйте позже.'

        elif code == 300:
            en_msg = ''
            ru_msg = 'Техническая ошибка. Повторите платеж позже.'

        elif code == 303:
            en_msg = ''
            ru_msg = 'Неверный номер телефона — должно быть 10 цифр'

        elif code == 319:
            en_msg = ''
            ru_msg = 'Ваш статус кошелька не позволяет совершить платеж. Повысьте статус кошелька: ' \
                     'укажите паспортные данные.'

        elif code == 407:
            en_msg = ''
            ru_msg = 'Недостаточно средств на вашей карте'

        elif code == 408:
            en_msg = ''
            ru_msg = 'У вас уже есть такой платеж — оплатите или отмените его'

        elif code == 455:
            en_msg = ''
            ru_msg = 'Платеж невозможен из-за ограничений на минимальный остаток'

        elif code == 461:
            en_msg = ''
            ru_msg = 'Время подтверждения операции истекло. Попробуйте еще раз.'

        elif code == 472:
            en_msg = ''
            ru_msg = 'Недостаточно денег на кошельке — пополните его'

        elif code == 500:
            en_msg = ''
            ru_msg = 'Техническая ошибка на стороне банка-получателя. Обратитесь в их поддержку.'

        elif code == 522:
            en_msg = ''
            ru_msg = 'Неверный номер или срок действия карты получателя. Проверьте данные и повторите попытку.'

        elif code == 547:
            en_msg = ''
            ru_msg = 'Неверный срок действия карты получателя. Проверьте данные и повторите попытку.'

        elif code == 548:
            en_msg = ''
            ru_msg = 'Истек срок действия карты получателя'

        elif code == 558:
            en_msg = ''
            ru_msg = 'Сумма платежа превышает максимально допустимую'

        elif code == 561:
            en_msg = ''
            ru_msg = 'Банк, куда вы переводите деньги, не принимает платеж. Обратитесь в его поддержку.'

        elif code == 700:
            en_msg = ''
            ru_msg = 'Превышен лимит для вашего статуса кошелька. Повысьте статус или уточните свой ' \
                     'текущий лимит в разделе Профиль.'

        elif code == 702:
            en_msg = ''
            ru_msg = 'Платеж невозможен из-за ограничений у получателя. Превышен его лимит на остаток. ' \
                     'Получателю необходимо связаться с нашей поддержкой.'

        elif code == 704:
            en_msg = ''
            ru_msg = 'Превышен ежемесячный лимит по вашему кошельку. Чтобы снять ограничения, ' \
                     'повысьте статус кошелька в Профиле.'

        elif code == 705:
            en_msg = ''
            ru_msg = 'Превышен ежемесячный лимит по вашему кошельку. Чтобы снять ограничения, ' \
                     'повысьте статус кошелька в Профиле.'

        elif code == 710:
            en_msg = ''
            ru_msg = 'Перевод невозможен – превышен лимит платежей за неделю в пользу одного и того же получателя'

        elif code == 711:
            en_msg = ''
            ru_msg = 'Перевод невозможен. Вы превысили лимит платежей для таких операций за месяц.'

        elif code == 716:
            en_msg = ''
            ru_msg = 'Вы превысили месячный лимит на снятие денег с карты. Чтобы снять ограничения, ' \
                     'повысьте статус кошелька в Профиле.'

        elif code == 717:
            en_msg = ''
            ru_msg = 'Вы превысили дневной лимит на снятие денег с карты. Чтобы снять ограничения, ' \
                     'повысьте статус кошелька в Профиле.'

        elif code == 746:
            en_msg = ''
            ru_msg = 'Перевод невозможен – превышен лимит в пользу одного и того же получателя'

        elif code == 747:
            en_msg = ''
            ru_msg = 'Перевод невозможен. Превышено количество операций в пользу одного и того же получателя.'

        elif code == 749:
            en_msg = ''
            ru_msg = 'Техническая ошибка. Обратитесь в нашу поддержку.'

        elif code == 750:
            en_msg = ''
            ru_msg = 'Техническая ошибка. Повторите платеж позже.'

        elif code == 757:
            en_msg = ''
            ru_msg = 'Превышен лимит на количество платежей. ' \
                     'Чтобы снять ограничения, повысьте статус кошелька в Профиле.'

        elif code == 797:
            en_msg = ''
            ru_msg = 'Платеж был отменен, деньги возвращены на ваш кошелек'

        elif code == 852:
            en_msg = ''
            ru_msg = 'Перевод невозможен – превышен лимит в пользу одного и того же получателя'

        elif code == 866:
            en_msg = ''
            ru_msg = 'Платеж не проведен. Превышен лимит 5 000 RUB — на исходящие переводы из RUB, USD, EUR в KZT ' \
                     'в месяц. Повысьте статус кошелька в Профиле и платите без ограничений.'

        elif code == 867:
            en_msg = ''
            ru_msg = 'Платеж не проведен. Превышен лимит 5 000 RUB — на входящие переводы из RUB, USD, EUR в KZT ' \
                     'в месяц. Повысьте статус кошелька в Профиле и платите без ограничений.'

        elif code == 893:
            en_msg = ''
            ru_msg = 'Перевод отклонен. Истек его срок действия.'

        elif code == 901:
            en_msg = ''
            ru_msg = 'Истек срок действия кода для подтверждения платежа. Повторите платеж.'

        elif code == 943:
            en_msg = ''
            ru_msg = 'Превышен лимит на переводы в месяц. Повысьте статус кошелька в Профиле' \
                     ' и переводите без ограничений.'

        elif code == 1050:
            en_msg = ''
            ru_msg = 'Превышен лимит на такие операции. Повысьте статус кошелька в Профиле ' \
                     'и расширьте свои возможности.'

        elif code == 7000:
            en_msg = ''
            ru_msg = 'Платеж отклонен. Проверьте реквизиты карты и повторите платеж.'

        elif code == 7600:
            en_msg = ''
            ru_msg = 'Платеж отклонен. Обратитесь в банк, выпустивший карту.'

        else:
            en_msg = 'Exception, status code {}'.format(code)
            ru_msg = 'Ошибка, статус код {}'.format(code)

        if self.exc_lang.lower() == 'ru':
            return QIWIAPIError(ru_msg)
        else:
            return QIWIAPIError(en_msg)

    def price_error(self, comment: str, need: int, paid: int) -> PriceError:  # todo en lang
        ru_msg = 'До оплаты не хватает {} руб.'.format(round(need - paid), 2)
        en_msg = ''

        if self.exc_lang.lower() == 'ru':
            return PriceError(comment=comment, need=need, paid=paid, mes=ru_msg)
        else:
            return PriceError(comment=comment, need=need, paid=paid, mes=en_msg)
