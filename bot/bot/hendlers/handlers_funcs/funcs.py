import random
import time

from typing import Tuple, Dict, Any
from aiogram.types import Message
from telethon.tl.types import User, Chat, Channel
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.storage import FSMContextProxy

from QIWI_API.errors import QIWIAPIError, PriceError
from db import get_user_by_telegram_id_stmt, async_mian_session, update_user_stmt
from loader import TELETON_CLIENT, qiwi_api
from utils.parsers.VK_parser import get_group
from utils.parsers.Telegram_parser import get_entity


async def check_subscription_and_add_to_cache(id_user: int, state: FSMContext) -> Tuple[bool, bool]:
    """
    First return main subs, second - test subs. Add user to cache.
    """

    async with state.proxy() as data:
        check = data.get(id_user)

        if not check:
            stmt = get_user_by_telegram_id_stmt(id_user)

            res = await async_mian_session.execute(stmt)

            user_db = res.one_or_none()
            user = {}

            for key in user_db.keys():
                user[key] = user_db[key]

            data[id_user] = user

        check_subscription = data.get(id_user, {}).get('subscription')
        check_test_period = data.get(id_user, {}).get('subscription_test_period')

        return check_subscription, check_test_period


async def build_slot_indexes(groups: set[Tuple[str, str]], data: FSMContextProxy) -> str:
    current_groups = []
    slots_dict = {}
    index = 1

    for group in groups:
        slots_dict[index] = group
        current_groups.append(
            '<b>~ /{index} ==> <a href="{url}">{name}</a></b>'.format(
                index=index,
                name=group[0],
                url=group[1]
            )
        )

        index += 1

    data['slot_indexes'] = slots_dict

    msg = 'У вас используются все слоты. Вы можете выбрать слот с группой для удаления\n\n{}'.format(
        '\n\n'.join(current_groups)
    )
    return msg


async def check_group(text: str) -> str | Dict[str, str | int]:
    url = text

    if url.startswith('https://t.me/'):
        type_ = 'telegram'
        entity: User | Chat | Channel | str = await get_entity(TELETON_CLIENT, url)

        if entity == 'Closed':
            return 'Closed'
        elif entity == 'Not found':
            return 'Not found'
        else:
            entity: Dict = entity.to_dict()

            name_ = entity.get('title', None)

            user_name = None if name_ else entity.get('username', entity.get('first_name'))

            if not name_:
                name_ = user_name

            id_ = entity.get('id')

            group = {
                'id': id_,
                'name': name_,
                'type': type_,
                'url': url,
                'user_name': user_name
            }
            return group

    elif url.startswith('https://vk.com/'):
        type_ = 'vk'

        simple_name = url.split('/')[-1]

        group_check = await get_group(simple_name)

        if group_check == 'Bad':
            return 'Bad'
        elif group_check == 'Closed':
            return 'Closed'
        elif group_check == 'Cant see all posts':
            return 'Cant see all posts'
        else:
            id_, name_ = group_check
            group = {
                'id': id_,
                'name': name_,
                'type': type_,
                'url': url
            }
            return group
    else:
        return 'Bad'


async def update_groups_count(user_id: int, data: FSMContextProxy) -> None:
    main_groups: set[str] = set()
    send_to_groups: set[str] = set()

    rls = data.get('rls')

    for row in rls.values():
        main_group = row.get('main_group_name')
        send_to_group = row.get('send_to_group_name')

        main_groups.add(main_group)
        send_to_groups.add(send_to_group)

    main_groups_count = len(main_groups)
    send_to_groups_count = len(send_to_groups)

    data['search_group_count'] = main_groups_count
    data['send_group_count'] = send_to_groups_count

    user = data.get(user_id)
    stmt = update_user_stmt(user)

    await async_mian_session.execute(stmt)
    await async_mian_session.commit()


async def pay_process(bill: Dict[str, Any], message: Message):
    for _ in range(3):
        try:
            if _check_payment(bill):
                return True

        except PriceError as p_exc:
            exc_mes = 'Упс, произошла ошибка:\n{}'.format(p_exc.mes)
            await message.answer(exc_mes)
            await pay_process(bill, message)

        except QIWIAPIError as q_exc:
            exc_mes = 'Упс, произошла ошибка:\n{}'.format(q_exc.args)
            await message.answer(exc_mes)
    else:
        return False


def _check_payment(bill: Dict[str, Any]) -> bool:
    remained_time = 10 * 60  # 10~15 min.

    while remained_time:
        if qiwi_api.check_payment(bill):
            return True

        time.sleep(random.uniform(1, 1.5))
        remained_time -= 1

    else:
        return False
