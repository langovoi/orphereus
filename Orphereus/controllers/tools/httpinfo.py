from pylons.i18n import N_
from string import *

from Orphereus.lib.BasePlugin import BasePlugin
from Orphereus.lib.base import *
from Orphereus.model import *

import logging
log = logging.getLogger(__name__)

class HTTPInfoPlugin(BasePlugin):
    def __init__(self):
        config = {'name' : N_('HTTP headers dumper'),
                 }

        BasePlugin.__init__(self, 'httpinfo', config)

    # Implementing BasePlugin
    def initRoutes(self, map):
        map.connect('/uaInfo', controller = 'tools/httpinfo', action = 'uaInfo')

# this import MUST be placed after public definitions to avoid loop importing
from Orphereus.controllers.OrphieBaseController import OrphieBaseController

class HttpinfoController(OrphieBaseController):
    def __init__(self):
        OrphieBaseController.__before__(self)

    def uaInfo(self):
        out = ''
        response.headers['Content-type'] = "text/plain"
        for key in request.environ.keys():
            if 'HTTP' in key or 'SERVER' in key or 'REMOTE' in key:
                out += key + ':' + request.environ[key] + '\n'
        out += 'test:' + str(request.POST.get('test', ''))
        return filterText(out)

