import cgi
import os.path

from paste.urlparser import StaticURLParser
from pylons.middleware import error_document_template, media_path
from OrphieBaseController import OrphieBaseController
from fc.lib.base import *

class ErrorController(BaseController):
    def document(self):
        """Render the error document"""
        params = dict(prefix=request.environ.get('SCRIPT_NAME', ''),
                 code=cgi.escape(request.params.get('code', '')),
                 message=cgi.escape(request.params.get('message', '')),
                 errorPic="%s/error.png" % g.OPT.staticPathWeb,
                 )
        #page = error_document_template % params
        #return page
        out = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
    <head>
        <title>Orphereus: misfunction</title>
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
        <META NAME="ROBOTS" CONTENT="NOARCHIVE">
        <link rel="shortcut icon" type="image/x-icon" href="/favicon.ico" />
    </head>
    <body style='background-color: #eb6d00;'>
    <div style="text-align:center;">
        <img src='%(errorPic)s' alt = 'Orphie-kun' style="border: 2px solid #820000;"/>
        <h1 style='color: #ffffff;'>I'm awfully sorry, my dear user.</h1>
        <h2 style='color: #ffffff;'>I'm feeling</h2>
        <h1 style="color: #820000; background-color: #FADDDD;">%(message)s/%(code)s</h1>
        <br/>
        %(prefix)s
    </div>
    </body>
</html>
"""
        out = out % params
        return out
    
