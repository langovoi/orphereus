import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import eagerload
from sqlalchemy.sql import and_, or_, not_

from fc.model import meta
from fc.model.Picture import Picture
from fc.model.Tag import Tag
from fc.model.LogEntry import LogEntry
from fc.lib.miscUtils import getRPN
from fc.lib.constantValues import *
import datetime

from pylons.i18n import _, ungettext, N_

import logging
log = logging.getLogger(__name__)

from fc.model import meta

t_posts = sa.Table("posts", meta.metadata,
    sa.Column("id"       , sa.types.Integer, primary_key=True),
    sa.Column("secondaryIndex",sa.types.Integer, nullable=True),
    sa.Column("parentid" , sa.types.Integer, sa.ForeignKey('posts.id'), index=True),
    sa.Column("message"  , sa.types.UnicodeText, nullable=True),
    sa.Column("messageShort", sa.types.UnicodeText, nullable=True),
    sa.Column("messageRaw"  , sa.types.UnicodeText, nullable=True),
    sa.Column("messageInfo"  , sa.types.UnicodeText, nullable=True),
    sa.Column("title"    , sa.types.UnicodeText, nullable=True),
    sa.Column("sage"     , sa.types.Boolean, nullable=True),
    sa.Column("uidNumber",sa.types.Integer,nullable=True),
    sa.Column("picid"    , sa.types.Integer, sa.ForeignKey('piclist.id')),
    sa.Column("date"     , sa.types.DateTime, nullable=False),
    sa.Column("bumpDate", sa.types.DateTime, nullable=True),
    sa.Column("spoiler"  , sa.types.Boolean, nullable=True),
    sa.Column("replyCount" , sa.types.Integer, nullable=False, server_default='0'),
    sa.Column("removemd5"  , sa.types.String(32), nullable=True),
    )

#TODO: rewrite Post
class Post(object):
    def __init__(self):
        self.date = datetime.datetime.now()

    @staticmethod
    def create(postParams):
        post = Post()
        post.message = postParams.message
        post.messageShort = postParams.messageShort
        post.messageRaw = postParams.messageRaw
        post.messageInfo = postParams.messageInfo
        post.title = postParams.title
        post.spoiler = postParams.spoiler
        post.uidNumber = postParams.uidNumber
        if postParams.removemd5:
            post.removemd5 = postParams.removemd5

        thread = postParams.thread
        if thread:
            post.parentid = thread.id
            thread.replyCount += 1
            post.sage = postParams.postSage
            if not postParams.postSage:
                thread.bumpDate = datetime.datetime.now()
        else:
            post.parentid = -1
            post.replyCount = 0
            post.bumpDate = datetime.datetime.now()
            post.tags = postParams.tags

        if not postParams.existentPic:
            picInfo = postParams.picInfo
            if picInfo:
                post.file = Picture.create(picInfo.relativeFilePath,
                                     picInfo.thumbFilePath,
                                     picInfo.fileSize,
                                     picInfo.sizes,
                                     picInfo.extId,
                                     picInfo.md5)
        else:
            post.picid = postParams.existentPic.id

        meta.Session.add(post)
        meta.Session.commit()
        return post

    def incrementStats(self):
        taglist = self.tags

        newThread = True
        if not taglist:
            taglist = self.parentPost.tags
            newThread = False

        for tag in taglist:
            tag.replyCount += 1
            if newThread:
                tag.threadCount += 1

    def selfModeratable(self):
        if getattr(self, 'smCached', None) == None:
            self.smCached = False
            for tag in self.tags:
                if tag.options and tag.options.selfModeration:
                    self.smCached = True
                    break
        return self.smCached

    def getExactReplyCount(self):
        if self.parentPost:
            return False
        else:
            return Post.query.filter(Post.parentid == self.id).count()

    def getReplies(self):
        if self.parentPost:
            return False
        else:
            return Post.query.filter(Post.parentid == self.id).all()

    @staticmethod
    def getPost(id):
        return Post.query.get(id)
        #return Post.query.filter(Post.id==id).one()

    @staticmethod
    def pictureRefCount(picid):
        return Post.query.filter(Post.picid==picid).count()

    @staticmethod
    def filterByUid(uidNumber):
        return Post.query.filter(Post.uidNumber == uidNumber)

    @staticmethod
    def filter(filter):
        return Post.query.filter(filter)

    @staticmethod
    def buildFilter(url, userInst):
        def buildMyPostsFilter():
            list  = []
            posts = Post.filterByUid(userInst.uidNumber).all()

            for p in posts:
                if p.parentid == -1 and not p.id in list:
                    list.append(p.id)
                elif p.parentid > -1 and not p.parentid in list:
                    list.append(p.parentid)
            return Post.id.in_(list)

        def buildArgument(arg):
            if not isinstance(arg, sa.sql.expression.ClauseElement):
                if arg == '@':
                    return (buildMyPostsFilter(), [])
                elif arg == '~':
                    return (not_(Post.tags.any(Tag.id.in_(userInst.homeExclude()))), [])
                else:
                    return (Post.tags.any(tag=arg), [arg])
            else:
                return arg

        filter = Post.query.options(eagerload('file')).filter(Post.parentid==-1)
        filteringExpression = False
        if not userInst.isAdmin():
            blocker = Post.tags.any(Tag.id.in_(meta.globj.forbiddenTags))
            blockHidden = not_(or_(blocker, Post.parentPost.has(blocker)))
            filteringExpression = blockHidden
        #log.debug(self.userInst.homeExclude())
        tagList = []
        if url:
            operators = {'+':1, '-':1, '^':2, '&':2}
            url = url.replace('&amp;', '&')
            RPN = getRPN(url,operators)
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
            if stack and isinstance(stack[0][0],sa.sql.expression.ClauseElement):
                cl = stack.pop()
                if filteringExpression:
                    filteringExpression = and_(cl[0], filteringExpression)
                else:
                    filteringExpression = cl[0]
                tagList = cl[1]
        filter = filter.filter(filteringExpression)
        return (filter, tagList, filteringExpression)

#    @staticmethod
#    def excludeAdminTags(filter, userInst):
#
#        return filter

    def deletePost(self, userInst, fileonly=False, checkOwnage=True, reason = "???", rempPass = False):
        opPostDeleted = False

        if userInst.Anonymous and self.removemd5 != rempPass:
            return False

        threadRemove = True
        tags = self.tags
        parentp = self
        if self.parentPost:
            parentp = self.parentPost
            tags = parentp.tags
            threadRemove = False

        isOwner = userInst.uidNumber == self.uidNumber
        selfModEnabled = parentp.selfModeratable()
        canModerate = selfModEnabled and userInst.uidNumber == parentp.uidNumber
        postCanBeDeleted = (isOwner or canModerate or userInst.canDeleteAllPosts())

        if checkOwnage and not postCanBeDeleted:
            # print some error stuff here
            return False

        tagline = u''
        taglist = []
        for tag in tags:
            taglist.append(tag.tag)

            tag.replyCount -= 1
            if threadRemove:
                tag.threadCount -= 1
        tagline = ', '.join(taglist)

        postOptions = Tag.conjunctedOptionsDescript(self.parentid>0 and parentp.tags or self.tags)
        if checkOwnage and not self.uidNumber == userInst.uidNumber:
            logEntry = u''
            if self.parentid > 0:
                logEntry = N_("Deleted post %s (owner %s); from thread: %s; tagline: %s; reason: %s") % (self.id, self.uidNumber, self.parentid, tagline, reason)
            else:
                logEntry = N_("Deleted thread %s (owner %s); tagline: %s; reason: %s") % (self.id, self.uidNumber, tagline, reason)
            if fileonly:
                logEntry += " %s" % N_("(file only)")
            LogEntry.create(userInst.uidNumber, LOG_EVENT_POSTS_DELETE, logEntry)

        if not self.parentPost and not fileonly:
            if not (postOptions.canDeleteOwnThreads or userInst.canDeleteAllPosts()):
                return False
            opPostDeleted = True
            for post in Post.query.filter(Post.parentid==self.id).all():
                post.deletePost(userInst, checkOwnage=False)

        pic = Picture.getPicture(self.picid)
        if pic:
            pic.deletePicture(True)
            pic = True

        if fileonly and postOptions.imagelessPost:
            if pic:
                self.picid = -1
        else:
            invisBumpDisabled = (meta.globj.settingsMap['invisibleBump'].value == 'false')
            parent = self.parentPost
            if parent:
                parent.replyCount -= 1

            if invisBumpDisabled and self.parentid != -1:
                thread = Post.query.filter(Post.parentid==self.parentid).all()
                if thread and thread[-1].id == self.id: #wut?
                    if len(thread) > 1 and not thread[-2].sage:
                        parent.bumpDate = thread[-2].date
                    else:
                        parent.bumpDate = parent.date
            meta.Session.delete(self)
        meta.Session.commit()
        return opPostDeleted
