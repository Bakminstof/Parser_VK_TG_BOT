import logging.config
import random
import re
import requests
import threading
import time

from uuid import uuid4
from typing import Callable, Dict, Any, List, Tuple

from .errors import ExceptionFactory  # Default
# from .logging import dict_config  # Default
from utils.logging import dict_config  # Custom

logging.config.dictConfig(dict_config)
qiwi_api_logger = logging.getLogger('qiwi_api_logger')


class QIWIApi:
    def __init__(self, token: str, phone: str, delay: Tuple[int | float, int | float] = (1, 1.5)) -> None:
        self.token = token

        self.phone = phone

        self.delay_range = delay

        self.__exc_factory = ExceptionFactory()

        self.__on_event = None

        self.__last_trx_ids = set()

        self.__thread: threading.Thread | None = None
        self.__start_thread = False
        self.__lock = threading.Lock()

        self.__session = requests.Session()

        self._main_url = 'https://edge.qiwi.com'

        self.__session.headers['Accept'] = 'application/json'
        self.__session.headers['Content-Type'] = 'application/json'
        self.__session.headers['Authorization'] = 'Bearer ' + self.token

        self.user: dict = {}

        self.__in_txn: Dict[str, List[Dict[str, str | int]]] = {}  # Incoming transactions with comments

        self.__get_user_info()

    def __thread_loop(self, target: Callable) -> None:
        log_msg = 'Start thread loop'
        qiwi_api_logger.debug(log_msg)

        while self.__start_thread:
            try:
                self.__lock.acquire()

                target()

            finally:
                self.__lock.release()

    def __get_user_info(self) -> None:
        url = self._main_url + '/person-profile/v1/profile/current'

        response = self.__session.get(url=url)

        if response.status_code != 200:
            exc = self.__exc_factory.http_error(code=response.status_code)

            log_msg = '-{name}- `{code}`: {mes}'.format(
                name=exc.__class__.__name__,
                code=response.status_code,
                mes=exc.mes
            )
            qiwi_api_logger.error(log_msg)

            raise exc

        json_res = response.json()

        user_id = json_res['authInfo']['personId']

        self.user['id'] = user_id

        log_msg = 'Get user info'
        qiwi_api_logger.debug(log_msg)

    def __get_limits(self) -> None:
        url = self._main_url + '/qw-limits/v1/persons/{person_id}/actual-limits'.format(
            person_id=self.user.get('id')
        )

        params = {
            'types': [
                'REFILL',
                'TURNOVER',
                'PAYMENTS_P2P',
                'PAYMENTS_PROVIDER_INTERNATIONALS',
                'PAYMENTS_PROVIDER_PAYOUT',
                'WITHDRAW_CASH'
            ]
        }

        response = self.__session.get(url=url, params=params)

        if response.status_code != 200:
            exc = self.__exc_factory.http_error(code=response.status_code)

            log_msg = '-{name}- `{code}`: {mes}'.format(
                name=exc.__class__.__name__,
                code=response.status_code,
                mes=exc.mes
            )
            qiwi_api_logger.error(log_msg)

            raise exc

        self.user['limits'] = response.json()

        log_msg = 'Get user limits'
        qiwi_api_logger.debug(log_msg)

    def __get_full_balance(self) -> List[Dict[str, Any]]:
        url = self._main_url + '/funding-sources/v2/persons/{person_id}/accounts'.format(
            person_id=self.user.get('id')
        )

        response = self.__session.get(url=url)

        if response.status_code != 200:
            exc = self.__exc_factory.http_error(code=response.status_code)

            log_msg = '-{name}- `{code}`: {mes}'.format(
                name=exc.__class__.__name__,
                code=response.status_code,
                mes=exc.mes
            )
            qiwi_api_logger.error(log_msg)

            raise exc

        response_json = response.json()

        balances = []

        for wallet in response_json['accounts']:
            if wallet['hasBalance']:
                balances.append({
                    'type': wallet['type'],
                    'balance': wallet['balance']
                })

        self.user['full_balance'] = balances

        log_msg = 'Get user full balance'
        qiwi_api_logger.debug(log_msg)

        return balances

    def __check_txn(self, bill_dict: Dict[str, Any], transaction: Dict[str, str | int], comment: str) -> None:
        txn_id: int = transaction['txnId']
        txn_error_code: int = transaction['errorCode']
        txn_status: str = transaction['status']
        txn_price: int = transaction['amount']

        current_price = bill_dict.get('price')

        if txn_error_code != 0:
            exc = self.__exc_factory.qiwi_api_error(code=txn_error_code)

            log_msg = '-{name}- `{code}`: {mes}'.format(
                name=exc.__class__.__name__,
                code=txn_error_code,
                mes=exc.mes
            )
            qiwi_api_logger.error(log_msg)

            raise exc
        else:
            if txn_status.lower() == 'success':
                txn_ids = bill_dict['txn_ids']

                if txn_price >= current_price:
                    bill_dict['success'] = True

                else:
                    if txn_id not in txn_ids:
                        bill_dict['paid'] = bill_dict.get('paid') + txn_price
                        paid = bill_dict.get('paid')

                        txn_ids.append(txn_id)
                        bill_dict['txn_ids'] = txn_ids

                        if paid >= current_price:
                            bill_dict['success'] = True
                        else:
                            exc = self.__exc_factory.price_error(comment, current_price, paid)

                            log_msg = '-{name}- `{code}`: {mes}'.format(
                                name=exc.__class__.__name__,
                                code=txn_error_code,
                                mes=exc.mes
                            )
                            qiwi_api_logger.error(log_msg)

                            raise exc

    def __get_incoming_payment_history(self) -> None:  # Get incoming transactions with comments
        url = self._main_url + '/payment-history/v2/persons/{wallet}/payments'.format(wallet=self.user.get('id'))

        params = {
            'rows': 30,
            'operation': 'IN'
        }

        response = self.__session.get(url=url, params=params)

        if response.status_code != 200:
            exc = self.__exc_factory.http_error(code=response.status_code)

            log_msg = '-{name}- `{code}`: {mes}'.format(
                name=exc.__class__.__name__,
                code=response.status_code,
                mes=exc.mes
            )
            qiwi_api_logger.error(log_msg)

            raise exc

        json_res = response.json()

        transactions = {}

        current_trx_ids = []

        for transaction in json_res['data']:
            user_comment: str = transaction['comment']

            if user_comment:
                user_comment = re.sub("^\s+|\n|\r|\s+$", '', user_comment)

                transaction_id = transaction['txnId']

                current_transaction = {
                    'txnId': transaction_id,
                    'errorCode': transaction['errorCode'],
                    'status': transaction['status'],
                    'comment': user_comment,
                    'amount': transaction['total']['amount']
                }

                if transactions.get(user_comment):
                    transactions_list = transactions.get(user_comment)
                    transactions_list.append(current_transaction)

                    transactions[user_comment] = transactions_list

                else:
                    transactions[user_comment] = [current_transaction]

                current_trx_ids.append(transaction_id)

                if transaction_id not in self.__last_trx_ids and self.__on_event is not None:
                    self.__on_event(current_transaction)

        if len(self.__last_trx_ids) >= 200:
            with self.__lock:
                self.__last_trx_ids.clear()

        self.__last_trx_ids.update(current_trx_ids)

        self.__in_txn = transactions

        time.sleep(random.uniform(*self.delay_range))

    def on_transaction(self):
        def decorator(func):
            self.__on_event = func

            if func.__code__.co_argcount != 1:
                exc = self.__exc_factory.arg_error()

                log_msg = '-{name}- `{code}`: {mes}'.format(
                    name=exc.__class__.__name__,
                    code='--',
                    mes=exc.mes
                )

                qiwi_api_logger.error(log_msg)

                raise exc

            log_msg = 'Set transaction event func'
            qiwi_api_logger.debug(log_msg)

        return decorator

    @classmethod
    def bill(cls, price: int, comment: str = str(uuid4()), currency=643) -> Dict[str, Any]:
        """
        Generates bill_dict

        :param comment: Comment
        :param price: Current price
        :param currency: Currency
        :return: Comment
        """
        bill_dict = {
            'id': comment,
            'price': price,
            'paid': 0,
            'txn_ids': [],
            'currency': currency,
            'success': False
        }

        return bill_dict

    def check_payment(self, bill_dict: Dict[str, Any]) -> bool:
        comment = bill_dict.get('id')

        if bill_dict['success']:
            log_msg = 'Successful payment. Bill: {}'.format(bill_dict)
            qiwi_api_logger.debug(log_msg)

            return True
        else:
            if comment in self.__in_txn.keys():
                transactions = self.__in_txn.get(comment)

                for txn in transactions:
                    self.__check_txn(bill_dict=bill_dict, transaction=txn, comment=comment)

            return False

    @property
    def full_balance(self) -> List[Dict[str, Any]]:
        """
        Returns full account balance info

        :return: balance (dict)
        """
        return self.__get_full_balance()

    @property
    def balance(self) -> List[float]:
        """
        Returns balances from all accounts

        :return: balances (list)
        """
        balances = self.full_balance
        balance = []

        for wallet in balances:
            if wallet['balance'] is not None:
                balance.append(wallet['balance']['amount'])

        return balance

    def start(self) -> None:
        """
        Starts thread
        """
        if not self.__start_thread:
            self.__start_thread = True

            self.__thread = threading.Thread(
                target=self.__thread_loop,
                args=(self.__get_incoming_payment_history,)
            )
            self.__thread.start()

            log_msg = 'Start QIWI API'
            qiwi_api_logger.debug(log_msg)

    def stop(self) -> None:
        """
        Stops thread
        """
        self.__start_thread = False

        log_msg = 'Stop QIWI API'
        qiwi_api_logger.warning(log_msg)
