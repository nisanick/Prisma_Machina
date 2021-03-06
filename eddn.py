import asyncio

import zlib
import zmq
from zmq.asyncio import Context

import sys
import time
import json
from types import SimpleNamespace
# import pyperclip

"""
 "  Configuration
"""
__relayEDDN = 'tcp://eddn.edcd.io:9500'
__timeoutEDDN = 600000

"""
 "  Start
"""


async def eddn(bot):
    context = Context.instance()
    subscriber = context.socket(zmq.SUB)
    
    subscriber.subscribe(b"")
    subscriber.set(zmq.RCVTIMEO, __timeoutEDDN)
    
    allowed_events = ['Location', 'FSDJump']
    
    bgs = bot.get_cog('BGS')

    while True:
        try:
            subscriber.connect(__relayEDDN)
            
            while True:
                __message = await subscriber.recv()
                
                if not __message:
                    subscriber.disconnect(__relayEDDN)
                    break
                
                __message = zlib.decompress(__message)
                if ("prismatic imperium" in str(__message).lower()
                        or "adamantine union" in str(__message).lower()
                        or "colonists of aurora" in str(__message).lower()):

                    __json = json.loads(__message, object_hook=lambda d: SimpleNamespace(**d))
                    message = __json.message
                    if message.event in allowed_events:
                        await bgs.submit(message)
        
        except zmq.ZMQError as e:
            print('ZMQSocketException: ' + str(e))
            sys.stdout.flush()
            subscriber.disconnect(__relayEDDN)
            time.sleep(5)
