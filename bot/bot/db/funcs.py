from copy import deepcopy
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from db.schemas import UsersTable, GroupsTable


def get_user_by_telegram_id_stmt(id_user: int):
    """
    SQL statement
    :return: SQL statement: user by telegram id
    """
    stmt = select(
        UsersTable.id,
        UsersTable.telegram_id,
        UsersTable.first_name,
        UsersTable.last_name,
        UsersTable.date_auth,
        UsersTable.subscription,
        UsersTable.subscription_test_period,
        UsersTable.date_start_subscription,
        UsersTable.date_end_subscription,
        UsersTable.total_subscription_days,
        UsersTable.search_group_count,
        UsersTable.send_group_count,
        UsersTable.additionally_search_group,
        UsersTable.additionally_send_group
    ).where(UsersTable.telegram_id == id_user)
    return stmt


def get_all_users_stmt():
    """
    SQL statement
    :return: SQL statement: all users
    """
    stmt = select(
        UsersTable.id,
        UsersTable.telegram_id,
        UsersTable.first_name,
        UsersTable.last_name,
        UsersTable.date_auth,
        UsersTable.subscription,
        UsersTable.subscription_test_period,
        UsersTable.date_start_subscription,
        UsersTable.date_end_subscription,
        UsersTable.total_subscription_days,
        UsersTable.search_group_count,
        UsersTable.send_group_count,
        UsersTable.additionally_search_group,
        UsersTable.additionally_send_group
    )
    return stmt


def get_all_rls_stmt():
    """
    SQL statement
    :return: SQL statement: all relationship
    """

    stmt = select(
        GroupsTable.id,
        GroupsTable.main_group_name,
        GroupsTable.main_group_url,
        GroupsTable.main_group_type,
        GroupsTable.main_group_id,
        GroupsTable.send_to_group_name,
        GroupsTable.send_to_group_url,
        GroupsTable.send_to_group_type,
        GroupsTable.send_to_group_id,
        GroupsTable.user_ids,
    )

    return stmt


def update_user_stmt(user: dict):
    """
    SQL statement
    :return: SQL statement: update user
    """
    to_update = deepcopy(user)

    insert_stmt = insert(UsersTable).values(**to_update)

    do_update_stmt = insert_stmt.on_conflict_do_update(
        index_elements=['id'],
        set_=to_update
    )

    del to_update

    return do_update_stmt
