################################################################################
#  Copyright (C) 2009 Johan Liebert, Mantycore, Hedger, Rusanon                #
#  < anoma.team@gmail.com ; http://orphereus.anoma.ch >                        #
#                                                                              #
#  This file is part of Orphereus, an imageboard engine.                       #
#                                                                              #
#  This program is free software; you can redistribute it and/or               #
#  modify it under the terms of the GNU General Public License                 #
#  as published by the Free Software Foundation; either version 2              #
#  of the License, or (at your option) any later version.                      #
#                                                                              #
#  This program is distributed in the hope that it will be useful,             #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of              #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
#  GNU General Public License for more details.                                #
#                                                                              #
#  You should have received a copy of the GNU General Public License           #
#  along with this program; if not, write to the Free Software                 #
#  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA. #
################################################################################

"""
Implements MCache class and it's fake copy, if memcache is unavailable. 
"""
try:
    from memcache import Client
except:
    Client = None

import logging
log = logging.getLogger(__name__)

if Client:
    class MCache(Client):
        valid = True
        uniqeKey = ''
        def __init__(self, *args, **kwargs):
            self.uniqeKey = kwargs.get('key', '')
            del kwargs['key']
            Client.__init__(self, *args, **kwargs)
            
        def set(self, key, val, **kwargs):
            return Client.set(self, self.uniqeKey+str(key), val, **kwargs)
        def get(self, key):
            #print ">%s" %(self.uniqeKey+str(key))
            return Client.get(self, self.uniqeKey+str(key))
            
else:
    class MCache():
        valid = False
        def __init__(self, *args, **kwargs):
            pass
        def set(self, *args, **kwargs):
            pass
        def get(self, *args, **kwargs):
            return None
        def set_multi(self, *args, **kwargs):
            pass
        def get_multi(self, *args, **kwargs):
            return {}

class CacheDict(dict):
    def setdefaultEx(self, key, function, *args):
        try:
            return self[key]
        except:
            log.debug("Key '%s' not found in cache, calling %s to fill in" %(key, function))
            return self.setdefault(key, function(*args))