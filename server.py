#!/usr/bin/env python

import asyncio
import datetime
import json
import logging
import websockets
import uuid
import time
from random import randint
from threading import Thread


USERS = set()
default_port = 1300
params = {}
LOOP = asyncio.get_event_loop()
th_stop = False
th = None


formatter = logging.Formatter('%(asctime)-15s %(message)s')
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('server.log')

c_handler.setFormatter(formatter)
f_handler.setFormatter(formatter)

logging.basicConfig(level=20, handlers=[c_handler, f_handler])
logger = logging.getLogger('server')


async def register(user):
    user.uuid = str(uuid.uuid1())
    user.service_port = default_port + 1 + len(USERS)
    user.custom_fields = set()
    user.results = []
    USERS.add(user)
    logger.info("Register: %s", user.uuid)


async def unregister(user):
    logger.info("Unregister: %s", user.uuid)
    USERS.remove(user)


def parse(message):
    return json.loads(message)


def build_container(type, value):
    return {'type': type, type: value}


async def _send(user, msg):
    if user and not user.closed:
        await user.send(json.dumps(msg))


def send_hit():
    global th_stop
    logger.info('Starting the Game')
    time.sleep(5)
    while not th_stop:
        msg = build_container('hit', {'date': datetime.datetime.now().isoformat(), 'x': randint(0, 640), 'y': randint(0, 480)})
        logger.info('Hit: %s' % msg)
        if USERS:
            for user in USERS:
                asyncio.run(_send(user, msg))
        time.sleep(5)


async def serve(websocket, path):
    global th, th_stop
    try:
        await register(websocket)
        th_stop = False
        if not th:
            th = Thread(target=send_hit, args=(), daemon=True)
            th.start()

        async for message in websocket:
            try:
                data = parse(message)
                if 'type' in data:
                    logger.info('Received %s from %s' % (message, websocket.uuid))
                    if data['type'] == "stop":
                        logger.info('Stopping the Game')
                        th_stop = True
                        await _send(websocket, build_container('status', 'DONE'))

            except Exception as pex:
                logger.error("Parsing Exception", pex)

    except Exception as ex:
        logger.error(ex)
    finally:
        await unregister(websocket)


_host = params.get('remote', 'localhost')
_port = params.get('port', default_port)

LOOP.run_until_complete(websockets.serve(serve, host=_host, port=_port))
logger.info("Started server %s:%s", _host, _port)
LOOP.run_forever()