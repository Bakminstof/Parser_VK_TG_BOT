import datetime
import sqlalchemy


from sqlalchemy import Column, INTEGER, VARCHAR, BOOLEAN, TIMESTAMP, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, BIGINT

from db.database import Base

sqlalchemy.sql.sqltypes._type_map[int] = BIGINT()


# tables
# users table
class UsersTable(Base):
    __tablename__ = 'users'

    id = Column(BIGINT(), primary_key=True)
    telegram_id = Column(BIGINT(), nullable=False, unique=True)
    first_name = Column(VARCHAR(50), nullable=False)
    last_name = Column(VARCHAR(50), default=None)

    date_auth = Column(TIMESTAMP, default=datetime.date.today())

    subscription = Column(BOOLEAN, default=False)
    subscription_test_period = Column(BOOLEAN, default=False)
    date_start_subscription = Column(TIMESTAMP, default=None)
    date_end_subscription = Column(TIMESTAMP, default=None)
    total_subscription_days = Column(INTEGER(), default=0)

    search_group_count = Column(INTEGER(), default=0)
    send_group_count = Column(INTEGER(), default=0)

    additionally_search_group = Column(INTEGER(), default=0)
    additionally_send_group = Column(INTEGER(), default=0)

    def __repr__(self) -> str:
        return 'id: {id}, ' \
               'telegram_id: {telegram_id}, ' \
               'first_name: {first_name}, ' \
               'last_name: {last_name}, ' \
               'date_auth: {date_auth}, ' \
               'date_start_subscription: {date_start_subscription}, ' \
               'date_end_subscription: {date_end_subscription}, ' \
               'subscription: {subscription}, ' \
               'subscription_test_period: {subscription_test_period}, ' \
               'total_subscription_days: {total_subscription_days}, ' \
               'search_group_count: {search_group_count}, ' \
               'send_group_count: {send_group_count}, ' \
               'additionally_search_group: {additionally_search_group}, ' \
               'additionally_send_group: {additionally_send_group}'.format(
            id=self.id,
            telegram_id=self.telegram_id,
            first_name=self.first_name,
            last_name=self.last_name,
            date_auth=self.date_auth,
            date_start_subscription=self.date_start_subscription,
            date_end_subscription=self.date_end_subscription,
            subscription=self.subscription,
            subscription_test_period=self.subscription_test_period,
            total_subscription_days=self.total_subscription_days,
            search_group_count=self.search_group_count,
            send_group_count=self.send_group_count,
            additionally_search_group=self.additionally_search_group,
            additionally_send_group=self.additionally_send_group,
        )

    def __str__(self):
        return self.__repr__()


# groups table
class GroupsTable(Base):
    __tablename__ = 'groups'
    __table_args__ = (
        UniqueConstraint(
            'main_group_url',
            'send_to_group_url',
            name='_group_uc'
        ),
    )

    id = Column(BIGINT(), primary_key=True)

    main_group_name = Column(VARCHAR(100), nullable=False)
    main_group_url = Column(VARCHAR(100), nullable=False)
    main_group_type = Column(VARCHAR(10), nullable=False)
    main_group_id = Column(BIGINT(), nullable=False)

    send_to_group_name = Column(VARCHAR(100), nullable=False)
    send_to_group_url = Column(VARCHAR(100), nullable=False)
    send_to_group_type = Column(VARCHAR(10), nullable=False)
    send_to_group_id = Column(BIGINT(), nullable=False)

    user_ids = Column(ARRAY(BIGINT))

    def __repr__(self) -> str:
        return 'id: {id}, ' \
               'main_group_name: {main_group_name}, ' \
               'main_group_url: {main_group_url}, ' \
               'main_group_type: {main_group_type}, ' \
               'main_group_id: {main_group_id}, ' \
               'send_to_group_name: {send_to_group_name}, ' \
               'send_to_group_url: {send_to_group_url}, ' \
               'send_to_group_type: {send_to_group_type}, ' \
               'send_to_group_id: {send_to_group_id}, ' \
               'user_ids: [{user_ids}]'.format(
            id=self.id,
            main_group_name=self.main_group_name,
            main_group_url=self.main_group_url,
            main_group_type=self.main_group_type,
            main_group_id=self.main_group_id,
            send_to_group_name=self.send_to_group_name,
            send_to_group_url=self.send_to_group_url,
            send_to_group_type=self.send_to_group_type,
            send_to_group_id=self.send_to_group_id,
            user_ids=self.user_ids,
        )

    def __str__(self):
        return self.__repr__()


# logs table
class BaseLoggerTable(Base):
    __tablename__ = 'base_logger'

    id = Column(BIGINT(), primary_key=True)
    level = Column(VARCHAR(20), nullable=False)
    name = Column(VARCHAR(100), nullable=False)
    dtime = Column(TIMESTAMP, nullable=False)
    line = Column(INTEGER(), nullable=False)
    message = Column(VARCHAR, nullable=False)
    except_text = Column(VARCHAR, default=None)

    def __repr__(self) -> str:
        return '(id: {id}, ' \
               'level: {level}, ' \
               'name: {name}, ' \
               'dtime: {dtime}, ' \
               'line: {line}, ' \
               'message: {message}, ' \
               'except_text: {except_text})'.format(
            id=self.id,
            level=self.level,
            name=self.name,
            dtime=self.dtime,
            line=self.line,
            message=self.message,
            except_text=self.except_text
        )
