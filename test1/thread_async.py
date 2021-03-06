from threading import Thread

import psycopg2
import select

import settings

DB_NAME = 'thread_async'


def wait(conn):
    while True:
        state = conn.poll()
        if state == psycopg2.extensions.POLL_OK:
            break
        elif state == psycopg2.extensions.POLL_WRITE:
            select.select([], [conn.fileno()], [])
        elif state == psycopg2.extensions.POLL_READ:
            select.select([conn.fileno()], [], [])
        else:
            raise psycopg2.OperationalError("poll() returned %s" % state)


def ainsert(data_range, tid, sleep):
    aconn = psycopg2.connect(
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        async_=1
    )
    wait(aconn)

    acurs = aconn.cursor()

    for id in data_range:
        acurs.execute(f"insert into {DB_NAME} values ({id},'{tid}');")
        wait(acurs.connection)

    acurs.close()
    aconn.close()


def run_ainsert():
    t1 = Thread(target=ainsert, args=(range(1, 9999), 1, 0.1))
    t2 = Thread(target=ainsert, args=(range(1, 9999), 2, 0.2))

    t1.start()
    t2.start()

    t1.join()
    t2.join()


run_ainsert()
