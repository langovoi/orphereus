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

log = logging.getLogger(__name__)

class FccController(BaseController):
    def __before__(self):
        self.userInst = FUser(session.get('uidNumber',-1))
        c.userInst = self.userInst
        c.currentURL = request.path_info
        if c.currentURL[-1] != '/':
            c.currentURL = c.currentURL + '/'
        if not self.userInst.isAuthorized():
            return redirect_to(c.currentURL+'authorize')
        if self.userInst.isBanned():
            return redirect_to('/youAreBanned')
        settingsDef = {
            "title" : "FailChan",
            "uploadPathLocal" : 'fc/public/uploads/',
            "uploadPathWeb" :  '/uploads/'
        }
        settings = meta.Session.query(Setting).all()
        settingsMap = {}
        if settings:
            for s in settings:
                if s.name in settingsDef:
                    settingsMap[s.name] = s
        for s in settingsDef:
            if not s in settingsMap:
                settingsMap[s] = Setting()
                settingsMap[s].name = s
                settingsMap[s].value = settingsDef[s]
                meta.Session.save(settingsMap[s])
                meta.Session.commit()        
        c.title = settingsMap['title'].value
        boards = meta.Session.query(Tag).join('options').filter(TagOptions.persistent==True).order_by(TagOptions.sectionId).all()
        c.boardlist = []
        sectionId = 0
        section = []
        for b in boards:
            if not sectionId:
                sectionId = b.options.sectionId
                section = []
            if sectionId != b.options.sectionId:
                c.boardlist.append(section)
                sectionId = b.options.sectionId
                section = []
            section.append(b.tag)
        if section:
            c.boardlist.append(section)
            
    def getRPN(self,text,operators):
        whitespace = [' ',"\t","\r","\n","'",'"','\\','<','>']
        stack = []
        temp  = []
        result= []
        for i in text:
            if i == '(':
                if temp:
                    result.append(''.join(temp))
                    temp = []
                stack.append('(')
            elif i == ')':
                if temp:
                    result.append(''.join(temp))
                    temp = []                
                while (stack and stack[-1] != '('):
                    result.append(stack.pop())
                if stack:
                    stack.pop()
            elif i in operators:
                if temp:
                    result.append(''.join(temp))
                    temp = []
                while (stack and (stack[-1] in operators) and (operators[i] <= operators[stack[-1]])):
                    result.append(stack.pop())
                stack.append(i)
            elif not i in whitespace:
                temp.append(i)
        if temp:
            result.append(''.join(temp))
            temp = []
        while stack:
            result.append(stack.pop())
        return result
        
    def buildFilter(self,url):
        def buildMyPostsFilter():
            list  = []
            posts = meta.Session.query(Post).filter(Post.uidNumber==self.userInst.uidNumber()).all()
            for p in posts:
                if p.parentid == -1 and not p.id in list:
                    list.append(p.id)
                elif p.parentid > -1 and not p.parentid in list:
                    list.append(p.parentid)
            return Post.id.in_(list)
            
        def buildArgument(arg):
            if not isinstance(arg,sqlalchemy.sql.expression.ClauseElement):
                if arg == '@':
                    return (buildMyPostsFilter(),[])
                elif arg == '~':
                    return (Post.parentid==-1,[])
                else:
                    return (Post.tags.any(tag=arg),[arg])
            else:
                return arg
         
        operators = {'+':1,'-':1,'^':2,'&':2}
        filter = meta.Session.query(Post).options(eagerload('file')).filter(Post.parentid==-1)
        tagList = []
        RPN = self.getRPN(url,operators)
        stack = []
        for i in RPN:
            if i in operators:
                # If operator is not provided with 2 arguments, we silently ignore it. (for example '- b' will be just 'b')
                if len(stack)>= 2:
                    arg2 = stack.pop()
                    arg1 = stack.pop()
                    if i == '+':
                        f = or_(arg1[0],arg2[0])
                        for t in arg2[1]:
                            if not t in arg1[1]:
                                arg1[1].append(t)
                        stack.append((f,arg1[1]))
                    elif i == '&' or i == '^':
                        f = and_(arg1[0],arg2[0])
                        for t in arg2[1]:
                            if not t in arg1[1]:
                                arg1[1].append(t)
                        stack.append((f,arg1[1])) 
                    elif i == '-':
                        f = and_(arg1[0],not_(arg2[0]))
                        for t in arg2[1]:
                            if t in arg1[1]:
                                arg1[1].remove(t)
                        stack.append((f,arg1[1]))                      
            else:
                stack.append(buildArgument(i))
        if stack and isinstance(stack[0][0],sqlalchemy.sql.expression.ClauseElement):
            cl = stack.pop()
            filter = filter.filter(cl[0])
            tagList = cl[1]
        return (filter,tagList)
        
    def showPosts(self, threadFilter, tempid='', page=0, board='', tags=[], tagList=[]):
        c.board = board
        c.uploadPathWeb = uploadPathWeb
        c.uidNumber = self.userInst.uidNumber()
        c.enableAllPostDeletion = self.userInst.canDeleteAllPosts()
        c.isAdmin = self.userInst.isAdmin()
        count = threadFilter.count()

        if count > 1:
            p = divmod(count, self.userInst.threadsPerPage())
            c.pages = p[0]
            if p[1]:
                c.pages += 1
            if (page + 1) > c.pages:
                page = c.pages - 1
            c.page = page
            c.threads = threadFilter.order_by(Post.bumpDate.desc())[(page * self.userInst.threadsPerPage()):(page + 1)* self.userInst.threadsPerPage()]
        elif count == 1:
            c.page  = False
            c.pages = False
            c.threads = [threadFilter.one()]
        elif count == 0:
            c.page  = False
            c.pages = False
            c.threads = []

        if tagList and len(tagList) == 1 and tags:
            currentBoard = tags[0]
            c.boardName = currentBoard.options and currentBoard.options.comment or ("/" + currentBoard.tag + "/")
        elif not tagList and tags:
            names = []
            for t in tags:
                names.append(t.options and t.options.comment or ("/" + t.tag + "/"))
            c.boardName = " + ".join(names)
        else:
            c.boardName = "/" + board + "/"
            
        c.boardOptions = self.conjunctTagOptions(tags)
        c.tagList = ' '.join(tagList)
            
        for thread in c.threads:
            if count > 1:
                replyCount = meta.Session.query(Post).options(eagerload('file')).filter(Post.parentid==thread.id).count()
                replyLim   = replyCount - self.userInst.repliesPerThread() 
                if replyLim < 0:
                    replyLim = 0
                thread.omittedPosts = replyLim
                thread.Replies = meta.Session.query(Post).options(eagerload('file')).filter(Post.parentid==thread.id).order_by(Post.id.asc())[replyLim:]
            else:
                thread.Replies = meta.Session.query(Post).options(eagerload('file')).filter(Post.parentid==thread.id).order_by(Post.id.asc()).all()
                thread.omittedPosts = 0
                
        if tempid:
            oekaki = meta.Session.query(Oekaki).filter(Oekaki.tempid==tempid).first()
            c.oekaki = oekaki
        else:
            c.oekaki = False
        
        c.returnToThread = session.get('returnToThread',False)

        return render('/%s.posts.mako' % self.userInst.template())
        
    def getParentID(self, id):
        post = meta.Session.query(Post).filter(Post.id==id).first()
        if post:
           return post.parentid
        else:
           return False
    
    def isPostOwner(self, id):
        post = meta.Session.query(Post).filter(Post.id==id).first()
        if post and post.uidNumber == self.userInst.uidNumber():
           return post.parentid
        else:
           return False

    def makeThumbnail(self, source, dest, maxSize):
        sourceImage = Image.open(source)
        size = sourceImage.size
        if sourceImage:
           sourceImage.thumbnail(maxSize,Image.ANTIALIAS)
           sourceImage.save(dest)
           return size + sourceImage.size
        else:
           return []

    def processFile(self, file, thumbSize=250):
        if isinstance(file,cgi.FieldStorage) or isinstance(file,FieldStorageLike):
           # We should check whether we got this file already or not
           # If we dont have it, we add it
           name = str(long(time.time() * 10**7))
           ext  = file.filename.rsplit('.',1)[:0:-1]
           if ext:
              ext = ext[0].lstrip(os.sep)
           else:
              # Panic, no extention found
              ext = ''
              return ''
           # Make sure its something we want to have
           extParams = meta.Session.query(Extension).filter(Extension.ext==ext).first()
           if not extParams:
              return ''

           localFilePath = os.path.join(uploadPath,name + '.' + ext)
           localFile = open(localFilePath,'w+b')
           shutil.copyfileobj(file.file, localFile)
           localFile.seek(0)
           md5 = hashlib.md5(localFile.read()).hexdigest()
           file.file.close()
           localFile.close()

           pic = meta.Session.query(Picture).filter(Picture.md5==md5).first()
           if pic:
               os.unlink(localFilePath)
               return pic

           if extParams.type == 'image':
              thumbFilePath = name + 's.' + ext
              size = self.makeThumbnail(localFilePath, os.path.join(uploadPath,thumbFilePath), (thumbSize,thumbSize))
           else:
               if extParams.type == 'image-jpg':
                  thumbFilePath = name + 's.jpg'
                  size = self.makeThumbnail(localFilePath, os.path.join(uploadPath,thumbFilePath), (thumbSize,thumbSize))
               else:
                  thumbFilePath = extParams.path
                  size = [0,0,extParams.thwidth,extParams.thheight]
           pic = Picture()
           pic.path = name + '.' + ext
           pic.thumpath = thumbFilePath
           pic.width = size[0]
           pic.height = size[1]
           pic.thwidth = size[2]
           pic.thheight = size[3]
           pic.extid = extParams.id
           pic.size = os.stat(localFilePath)[6]
           pic.md5 = md5
           meta.Session.save(pic)
           meta.Session.commit()
           return pic
        else:
           return None
           
    def conjunctTagOptions(self, tags):
        options = TagOptions()
        options.imagelessThread = True
        options.imagelessPost   = True
        options.images   = True
        options.enableSpoilers = True
        options.maxFileSize = 2621440
        options.minPicSize = 50
        options.thumbSize = 250
        for t in tags:
            if t.options:
                options.imagelessThread = options.imagelessThread & t.options.imagelessThread
                options.imagelessPost = options.imagelessPost & t.options.imagelessPost
                options.enableSpoilers = options.enableSpoilers & t.options.enableSpoilers
                options.images = options.images & t.options.images
                if t.options.maxFileSize < options.maxFileSize:
                    options.maxFileSize = t.options.maxFileSize
                if t.options.minPicSize > options.minPicSize:
                    options.minPicSize = t.options.minPicSize
                if t.options.thumbSize < options.thumbSize:
                    options.thumbSize = t.options.thumbSize                   
        return options
        
    def __getPostTags(self, tagstr):
            tags = []
            tagsl= []
            #maintag = request.POST.get('maintag',False)
            #if maintag and maintag != '~':
            #    tag = meta.Session.query(Tag).filter(Tag.tag==maintag).first()
            #    if tag:
            #        tags.append(tag)
            #    else:
            #        tags.append(Tag(maintag))
            #    tagsl.append(maintag)
            if tagstr:
                regex = re.compile(r"""([^,@~\#\+\-\&\s\/\\\(\)<>'"%\d][^,@~\#\+\-\&\s\/\\\(\)<>'"%]*)""")
                tlist = regex.findall(tagstr)
                for t in tlist:
                    if not t in tagsl:
                        tag = meta.Session.query(Tag).filter(Tag.tag==t).first()
                        if tag:
                            tags.append(tag)
                        else:
                            tags.append(Tag(t))
                        tagsl.append(t)      
            return tags
    
    def processPost(self, postid=0, board=u''):
        if postid:
            thePost = meta.Session.query(Post).filter(Post.id==postid).first()
            if thePost.parentid != -1:
               thread = meta.Session.query(Post).filter(Post.id==thePost.parentid).one()
            else:
               thread = thePost
            tags = thread.tags
        else:
            tagstr = request.POST.get('tags',False)
            tags = self.__getPostTags(tagstr)
            if not tags:
                c.errorText = "You should specify at least one board"
                return render('/wakaba.error.mako')
        options = self.conjunctTagOptions(tags)
        if not options.images and ((not options.imagelessThread and not postid) or (postid and not options.imagelessPost)):
            c.errorText = "Unacceptable combination of tags"
            return render('/wakaba.error.mako')
        
        post = Post()
        tempid = request.POST.get('tempid',False)
        post.message = request.POST.get('message', '')
        tempid = request.POST.get('tempid',False)
        if tempid:
           oekaki = meta.Session.query(Oekaki).filter(Oekaki.tempid==tempid).first()
           file = FieldStorageLike(oekaki.path,os.path.join(uploadPath,oekaki.path))
           post.message += "\r\nDrawn with **%s** in %s seconds" % (oekaki.type,str(int(oekaki.time/1000)))
           if oekaki.source:
              post.message += ", source >>%s" % oekaki.source
        else:
           file = request.POST.get('file',False)
        if post.message:
           parser = WakabaParser()
           post.message = parser.parseWakaba(post.message,self)     
        post.title = filterText(request.POST['title'])
        post.date = datetime.datetime.now()
        pic = self.processFile(file,options.thumbSize)
        if pic:
            if pic.size > options.maxFileSize:
                c.errorText = "File size exceeds the limit"
                return render('/wakaba.error.mako')
            if pic.height and (pic.height < options.minPicSize or pic.width < options.minPicSize):
                c.errorText = "Image is too small"
                return render('/wakaba.error.mako')
            if not options.images:
                c.errorText = "Files are not allowed on this board"
                return render('/wakaba.error.mako')
            post.picid = pic.id
        post.uidNumber = self.userInst.uidNumber()
        
        if not post.message and not post.picid:
            c.errorText = "At least message or file should be specified"
            return render('/wakaba.error.mako')
        
        if options.enableSpoilers:
            post.spoiler = request.POST.get('spoiler', False)  
            
        if postid:
            if not post.picid and not options.imagelessPost:
                c.errorText = "Replies without image are not allowed"
                return render('/wakaba.error.mako')
            post.parentid = thread.id
            post.sage = request.POST.get('sage', False)
            if not post.sage:
                thread.bumpDate = datetime.datetime.now()
        else:
            if not post.picid and not options.imagelessThread:
                c.errorText = "Threads without image are not allowed"
                return render('/wakaba.error.mako')        
            post.parentid = -1
            post.bumpDate = datetime.datetime.now()
            post.tags = tags
        meta.Session.save(post)
        meta.Session.commit()
        returnTo = request.POST.get('gb2', 'board')
        #response.set_cookie('returnTo', returnTo, expires=3600000)
        session['returnToThread'] = not (returnTo == 'board')
        session.save()
        if returnTo == 'board':             
            rboard = u'/'+tags[0].tag+u'/'
            redirect_to(rboard.encode('utf-8'))
        else:
            if postid:
                return redirect_to(action='GetThread',post=post.parentid,board=None)
            else:
                return redirect_to(action='GetThread',post=post.id,board=None)          

    def GetThread(self, post, tempid):
        thePost = meta.Session.query(Post).options(eagerload('file')).filter(Post.id==post).first()

        if thePost and thePost.parentid != -1:
            thePost = meta.Session.query(Post).options(eagerload('file')).filter(Post.id==thePost.parentid).first()
            
        if not thePost:
            c.errorText = "No such post exist."
            return render('/wakaba.error.mako')
            
        filter = meta.Session.query(Post).options(eagerload('file')).filter(Post.id==thePost.id)
        c.PostAction = thePost.id
        
        return self.showPosts(threadFilter=filter, tempid=tempid, page=0, board='', tags=thePost.tags)

    def GetBoard(self, board, tempid, page=0):
        board = filterText(board)
        c.PostAction = board
        
        filter = self.buildFilter(board)
        tags = meta.Session.query(Tag).options(eagerload('options')).filter(Tag.tag.in_(filter[1])).all()
        return self.showPosts(threadFilter=filter[0], tempid=tempid, page=int(page), board=board, tags=tags, tagList=filter[1])

    def PostReply(self, post):
        return self.processPost(postid=post)

    def PostThread(self, board):
        return self.processPost(board=board)
            

    def oekakiDraw(self,url):
        c.url = url
        c.uploadPathWeb = uploadPathWeb
        c.canvas = False
        c.width  = request.POST.get('oekaki_x','300')
        c.height = request.POST.get('oekaki_y','300')
        enablePicLoading = not (request.POST.get('oekaki_type','Reply') == 'New');        
        if not (isNumber(c.width) or isNumber(c.height)) or (int(c.width)<=10 or int(c.height)<=10):
           c.width = 300
           c.height = 300            
        c.tempid = str(long(time.time() * 10**7))
        oekaki = Oekaki()
        oekaki.tempid = c.tempid
        oekaki.picid = -1
        oekaki.time = -1
        if request.POST.get('oekaki_painter','shiNormal') == 'shiNormal':
            oekaki.type = 'Shi normal'
            c.oekakiToolString = 'normal';
        else:
            oekaki.type = 'Shi pro'
            c.oekakiToolString = 'pro'
        oekaki.uidNumber = session['uidNumber']
        oekaki.path = ''        
        oekaki.source = 0
        if isNumber(url) and enablePicLoading:
           post = meta.Session.query(Post).filter(Post.id==url).one()
           if post.picid:
              pic = meta.Session.query(Picture).filter(Picture.id==post.picid).first()
              if pic and pic.width:
                 oekaki.source = post.id
                 c.canvas = pic.path
                 c.width  = pic.width
                 c.height = pic.height
        meta.Session.save(oekaki)
        meta.Session.commit()
        return render('/spainter.mako')
    def DeletePost(self, post):
        fileonly = 'fileonly' in request.POST
        for i in request.POST:
            if re.compile("^\d+$").match(request.POST[i]):
                self.processDelete(request.POST[i],fileonly)
        return redirect_to(str('/%s' % post.encode('utf-8')))
    def processDelete(self, postid, fileonly=False, checkOwnage=True):
        p = meta.Session.query(Post).get(postid)
        if p:
            if checkOwnage and not (p.uidNumber == self.userInst.uidNumber() or self.userInst.canDeleteAllPosts()):
                # print some error stuff here
                return
            if p.parentid == -1 and not fileonly:
                for post in meta.Session.query(Post).filter(Post.parentid==p.id).all():
                    self.processDelete(postid=post.id,checkOwnage=False)
            pic = meta.Session.query(Picture).filter(Picture.id==p.picid).first()
            if pic and meta.Session.query(Post).filter(Post.picid==p.picid).count() == 1:
                filePath = os.path.join(uploadPath,pic.path)
                thumPath = os.path.join(uploadPath,pic.thumpath)
                if os.path.isfile(filePath): os.unlink(filePath)
                ext = meta.Session.query(Extension).filter(Extension.id==pic.extid).first()
                if not ext.path:
                    if os.path.isfile(thumPath): os.unlink(thumPath)
                meta.Session.delete(pic)
            if fileonly: p.picid = None
            else: meta.Session.delete(p)
        meta.Session.commit()
    def showProfile(self):
        c.templates = ['wakaba']
        c.styles    = ['photon']
        c.profileChanged = False
        if request.POST:
            template = request.POST.get('template',self.userInst.template())
            if template in c.templates:
                self.userInst.template(template)
            style = request.POST.get('style',self.userInst.style())
            if style in c.styles:
                self.userInst.style(style)
            threadsPerPage = request.POST.get('threadsPerPage',self.userInst.threadsPerPage())
            if isNumber(threadsPerPage) and (0 < int(threadsPerPage) < 100):
                self.userInst.threadsPerPage(threadsPerPage)
            repliesPerThread = request.POST.get('repliesPerThread',self.userInst.repliesPerThread())
            if isNumber(repliesPerThread) and (0 < int(repliesPerThread) < 100):
                self.userInst.repliesPerThread(repliesPerThread)
            c.profileChanged = True
            meta.Session.commit()
        c.userInst = self.userInst
        return render('/wakaba.profile.mako')
