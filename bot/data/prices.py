from typing import Tuple


# Стоимость в рублях
ONE_WEEK_GROUP_PRICE = 70 * 100  # Неделя (70 руб.)
ONE_MONTH_GROUP_PRICE = 200 * 100  # Месяц (200 руб.)
THREE_MONTHS_GROUP_PRICE = 560 * 100  # Три месяца (560 руб.)

# Стоимость в рублях
ONE_SLOT_PRICE = 20 * 100   # 1 шт. (20 руб.)
THREE_SLOTS_PRICE = 55 * 100  # 3 шт. (55 руб.)
FIVE_SLOTS_PRICE = 90 * 100  # 5 шт. (90 руб.)

# Процент за один слот группы (из которой брать или отправлять)
SLOT_PERCENT = 10  # %

# Базовое количество слотов
BASE_SLOTS_COUNT = 4


def current_slot_price(slot_price: int, subs_days: int, slots_count: int) -> int:
    """
    Return total price for add slots subscription in !COP! (1/100 RUB)
    """
    price_per_day = int(round(slot_price / 30, 2))
    total_price = price_per_day * subs_days * slots_count
    return total_price


def continue_subscription_price(base_price: int, slots_count: int = 0) -> Tuple[int, int, int]:
    """
    Return tuple prices (Total price, base price, slots price) in !RUB!
    """
    base_p = int(base_price / 100)
    slot_p = int(((base_price / 100) * SLOT_PERCENT * slots_count) / 100)

    total = base_p + slot_p

    return total, base_p, slot_p
