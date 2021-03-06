# -*- coding: utf-8 -*-
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

from Orphereus.lib.base import *
from Orphereus.lib.miscUtils import *
from Orphereus.lib.constantValues import *
from Orphereus.lib.fileHolder import AngryFileHolder
from Orphereus.model import *

import cgi
import shutil
import base64, hashlib
import logging
log = logging.getLogger(__name__)

class FileProcessingException(Exception):
    pass

class CantWriteExc(FileProcessingException):
    def __init__(self, msg):
        self.msg = msg

class NoExtension(FileProcessingException):
    pass

class ExtensionDisallowed(FileProcessingException):
    def __init__(self, ext):
        self.ext = ext

class BrokenPicture(FileProcessingException):
    pass

def processFile(file, thumbSize, baseEncoded):
    #log.debug('got file %s, dict: %s, test: %s' %(file, file.__dict__, isinstance(file, FieldStorageLike)))
    if isinstance(file, cgi.FieldStorage) or isinstance(file, FieldStorageLike):
        name = unixTs()
        ext = file.filename.rsplit('.', 1)[:0:-1]

        #ret: [FileHolder, PicInfo, Picture, Error]

        # We should check whether we got this file already or not
        # If we dont have it, we add it
        if ext:
            ext = ext[0].lstrip(os.sep).lower()
        else:    # Panic, no extention found
            #ext = ''
            #return [False, False, False, _("Can't post files without extension")]
            raise NoExtension()

        # Make sure its something we want to have
        extParams = Extension.getExtension(ext)
        if not extParams or not extParams.enabled:
            #return [False, False, False, _(u'Extension "%s" is disallowed') % ext]
            raise ExtensionDisallowed(ext)

        relativeFilePath = h.expandName('%s.%s' % (name, ext))
        localFilePath = os.path.realpath(os.path.join(meta.globj.OPT.uploadPath, relativeFilePath))
        targetDir = os.path.dirname(localFilePath)
        #log.debug(localFilePath)
        #log.debug(targetDir)

        try:
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            localFile = open(localFilePath, 'w+b')
            if not baseEncoded:
                shutil.copyfileobj(file.file, localFile)
            else:
                base64.decode(file.file, localFile)
            localFile.seek(0)
            md5 = hashlib.md5(localFile.read()).hexdigest()
            localFile.close()
        except Exception, e:
            log.error("Exception '%s' while saving file to '%s'" % (str(e), localFilePath))
            raise CantWriteExc(str(e))
        finally:
            file.file.close()

        fileSize = os.stat(localFilePath)[6]
        picInfo = empty()
        picInfo.localFilePath = localFilePath
        picInfo.relativeFilePath = relativeFilePath
        picInfo.fileSize = fileSize
        picInfo.md5 = md5
        picInfo.sizes = []
        picInfo.extension = extParams
        picInfo.animPath = None
        picInfo.relationInfo = None

        pic = Picture.getByMd5(md5)
        if pic:
            os.unlink(localFilePath)
            picInfo.sizes = [pic.width, pic.height, pic.thwidth, pic.thheight]
            picInfo.thumbFilePath = pic.thumpath
            picInfo.relativeFilePath = pic.path
            picInfo.localFilePath = os.path.join(meta.globj.OPT.uploadPath, picInfo.relativeFilePath)
            return [False, picInfo, pic, False]

        thumbFilePath = False
        localThumbPath = False
        try:
            #log.debug('Testing: %s' %extParams.type)
            if not extParams.type in ('image', 'image-jpg'):
                # log.debug('Not an image')
                thumbFilePath = extParams.path
                picInfo.sizes = [None, None, extParams.thwidth, extParams.thheight]
            elif extParams.type == 'image':
                thumbFilePath = h.expandName('%ss.%s' % (name, ext))
            else:
                thumbFilePath = h.expandName('%ss.jpg' % (name))
            localThumbPath = os.path.join(meta.globj.OPT.uploadPath, thumbFilePath)
            picInfo.thumbFilePath = thumbFilePath
            if not picInfo.sizes:
                picInfo.sizes = Picture.makeThumbnail(localFilePath, localThumbPath, (thumbSize, thumbSize))
        except Exception, e:
            log.warning("Exception in image thumbnail maker: %s" % str(e))
            try:
                os.unlink(localFilePath)
            except Exception, e:
                log.warning("can't remove incorrect file %s (%s)" % (localFilePath, str(e)))
            raise BrokenPicture()
            #return [False, False, False, _(u"Broken picture. Maybe it is interlaced PNG?")]

        return [AngryFileHolder((localFilePath, localThumbPath)), picInfo, False, False]
    else:
        return False

def safeFileProcess(file, thumbSize, baseEncoded, translateErrors):
        fileDescriptors = [False, False, False, False]
        tr = lambda x: x
        if translateErrors:
            tr = _
        try:
            fileDescriptors = processFile(file, thumbSize, baseEncoded)
        except FileProcessingException, e:
            msg = "Unknown file processing exception"
            if isinstance(e, CantWriteExc):
                msg = tr("Can't write to target path. Looks like improper engine configuration.")
            elif isinstance(e, NoExtension):
                msg = tr("Can't post files without extension")
            elif isinstance(e, ExtensionDisallowed):
                msg = tr(u'Extension "%s" is disallowed') % e.ext
            elif isinstance(e, BrokenPicture):
                msg = tr(u"Broken picture. Maybe it is interlaced PNG?")
            fileDescriptors[-1] = msg
        return fileDescriptors
