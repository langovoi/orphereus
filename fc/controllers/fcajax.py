import logging

from fc.lib.base import *
from fc.model import *
from sqlalchemy.orm import eagerload
from sqlalchemy.orm import class_mapper
from sqlalchemy.sql import and_, or_, not_
import sqlalchemy
import os
import cgi
import shutil
import datetime
import time
import Image
import os
import hashlib
import re
from wakabaparse import WakabaParser
from fc.lib.fuser import FUser
from fc.lib.miscUtils import *
from fc.lib.constantValues import *
from OrphieBaseController import OrphieBaseController

log = logging.getLogger(__name__)

class FcajaxController(OrphieBaseController):
    def __before__(self):
        OrphieBaseController.__before__(self)
        #self.userInst = FUser(session.get('uidNumber',-1))
        c.userInst = self.userInst
        if not self.userInst.isAuthorized() or self.userInst.isBanned():
            abort(403)
            
    def getPost(self, post):
        postInst = meta.Session.query(Post).get(post)
        if postInst:
            if postInst.parentid == -1:
                parent = postInst
            else:
                parent = meta.Session.query(Post).get(postInst.parentid)

            forbiddenTags = getTagsListFromString(g.settingsMap['adminOnlyTags'].value)       
            for t in parent.tags:
                if t.id in forbiddenTags and not self.userInst.isAdmin():
                    abort(403)
            return postInst.message
        else:
            abort(404)

    def getRenderedPost(self, post):
        postInst = meta.Session.query(Post).get(post)
        if postInst:
            if postInst.parentid == -1:
                parent = postInst
            else:
                parent = meta.Session.query(Post).get(postInst.parentid)

            forbiddenTags = getTagsListFromString(g.settingsMap['adminOnlyTags'].value)       
            for t in parent.tags:
                if t.id in forbiddenTags and not self.userInst.isAdmin():
                    abort(403)
                    
            #uncomment to disable folding for big posts
            #parent.enableShortMessages=False
            return self.render('postReply', thread=parent, post = postInst)
        else:
            abort(404)            
    
    def getRepliesCountForThread(self, post):
        postInst = meta.Session.query(Post).get(post)
        if postInst and postInst.parentid == -1:
            return str(meta.Session.query(Post).filter(Post.parentid == postInst.id).count())
        else:
            abort(404)
    
    def getThreadIds(self, post):
        postInst = meta.Session.query(Post).get(post)
        if postInst and postInst.parentid == -1:
            replies = meta.Session.query(Post).filter(Post.parentid == postInst.id).all()
            ret = [str(post)]
            if replies:
                for reply in replies:
                    ret.append(str(reply.id))
            return ','.join(ret)
        else:
            abort(404)
    
    def getUserSettings(self):
        return str(self.userInst.optionsDump())
    
    def editUserFilter(self,fid,filter):
        if self.userInst.Anonymous:
            abort(403)
        userFilter = meta.Session.query(UserFilters).get(fid)
        if not userFilter or userFilter.uidNumber != self.userInst.uidNumber():
            abort(404)
        userFilter.filter = filterText(filter)
        meta.Session.commit()
        return userFilter.filter
    
    def deleteUserFilter(self,fid):
        if self.userInst.Anonymous:
            abort(403)
        userFilter = meta.Session.query(UserFilters).get(fid)
        if not userFilter or userFilter.uidNumber != self.userInst.uidNumber():
            abort(404)
        meta.Session.delete(userFilter)
        meta.Session.commit()
        return ''
        
    def addUserFilter(self,filter):
        if self.userInst.Anonymous:
            abort(403)
        userFilter = UserFilters()
        userFilter.uidNumber = self.userInst.uidNumber()
        userFilter.filter = filterText(filter)
        meta.Session.save(userFilter)
        meta.Session.commit()
        c.userFilter = userFilter
        return self.render('ajax.addUserFilter') #render('/ajax.addUserFilter.mako')
    
    def hideThread(self,post,url):
        if self.userInst.Anonymous:
            abort(403)
        postInst = meta.Session.query(Post).get(post)
        if postInst:
            if postInst.parentid == -1:
                hideThreads = self.userInst.hideThreads()
                if not post in hideThreads:
                    hideThreads.append(post)
                    self.userInst.hideThreads(hideThreads)
                    meta.Session.commit()
        if url:
            return redirect_to(str('/%s' % url.encode('utf-8')))
        else:
            return ''
    
    def showThread(self,post,redirect):
        if self.userInst.Anonymous:
            abort(403)
        postInst = meta.Session.query(Post).get(post)
        if postInst:
            if postInst.parentid == -1:
                hideThreads = self.userInst.hideThreads()
                if post in hideThreads:
                    hideThreads.remove(post)
                    self.userInst.hideThreads(hideThreads)
                    meta.Session.commit()
        if redirect:
            return redirect_to(str('/%s' %redirect.encode('utf-8')))
        else:
            return ''
