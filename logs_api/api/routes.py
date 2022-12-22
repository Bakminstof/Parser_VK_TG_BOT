import asyncio
import flask.json

from flask import Flask, request
from sqlalchemy import select

from schemas import BaseLoggerTable
from database import a_session_log

CURRENT_LOG_ID: int = 0

app = Flask(__name__)


@app.route('/api/logs', methods=['GET'])
def collect_logs():
    first = request.args.get('first', type=int)

    global CURRENT_LOG_ID

    stmt = select(
        BaseLoggerTable.id,
        BaseLoggerTable.level,
        BaseLoggerTable.name,
        BaseLoggerTable.dtime,
        BaseLoggerTable.line,
        BaseLoggerTable.message,
        BaseLoggerTable.except_text
    )

    if first:
        result = asyncio.run(a_session_log.execute(stmt))
    else:
        result = asyncio.run(a_session_log.execute(stmt.filter(BaseLoggerTable.id > CURRENT_LOG_ID)))

    log_rows = result.all()

    logs = []

    for row in log_rows:
        id_ = row[0]

        log = {
            'log_id': id_,
            'log_level': row[1],
            'logger_name': row[2],
            'log_time': row[3],
            'log_line': row[4],
            'log_msg': row[5],
            'log_except_text': row[6]
        }

        logs.append(log)

        CURRENT_LOG_ID = id_

    return flask.json.dumps(logs), 200


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)
