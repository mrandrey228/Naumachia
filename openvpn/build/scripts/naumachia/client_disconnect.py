#!/usr/bin/env python3
"""
This script fires whenever a client disconnects from the VPN tunnel
It is called under the OpenVPN --client-disconnect option
When called this script will clean up the DB entries made by client-connect
"""

from common import get_env
from redis import StrictRedis
import logging

logging.basicConfig(level=logging.DEBUG)

def client_disconnect():
    env = get_env()
    client = '{TRUSTED_IP}:{TRUSTED_PORT}'.format(**env)
    redis = StrictRedis(host=env['REDIS_HOSTNAME'], db=env['REDIS_DB'], port=env['REDIS_PORT'], password=env['REDIS_PASSWORD'])

    connection_id = redis.hget('connections', client)
    if connection_id:
        connection_id = connection_id.decode('utf-8')
        user_id = redis.hget('connection:'+connection_id, 'user')
        if user_id:
            user_id = user_id.decode('utf-8')
            redis.srem('user:'+user_id+':connections', connection_id)
            if redis.scard('connections:'+user_id) == 0:
                redis.hset('user:'+user_id, 'status', 'disconnected')
        redis.hset('connection:'+connection_id, 'alive', 'no')
        redis.hdel('connections', client)
    else:
        logging.warn("Connection {} removed from Redis prior to disconnect".format(client))

if __name__ == "__main__":
    client_disconnect()
