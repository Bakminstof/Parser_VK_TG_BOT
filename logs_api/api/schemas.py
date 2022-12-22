from sqlalchemy import Column, INTEGER, VARCHAR, TIMESTAMP
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# tables
class BaseLoggerTable(Base):
    __tablename__ = 'base_logger'

    id = Column(INTEGER(), primary_key=True)
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
