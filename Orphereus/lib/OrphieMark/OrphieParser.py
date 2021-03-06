# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2009 Hedger                                                   #
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

from Orphereus.lib.OrphieMark.BlockFormatting import parseBlockFormattingElements
from Orphereus.lib.OrphieMark.tools import fixHtml, cutHtml

import logging
log = logging.getLogger(__name__)

def printTree(root, level = 0):
    shift = "  " * level

    print "%s%s" % (shift, root)
    for item in root.children:
        printTree(item, level + 1)

class OrphieParser(object):
    def __init__(self, globj, callbackSource):
        self.globj = globj
        self.callbackSource = callbackSource
        #log.debug(self.callbackSource)

    def parseMessage(self, messageText, parentId, maxLines, maxLen):
        rootElement = parseBlockFormattingElements(messageText)
        #printTree(rootElement)
        fullMessage = rootElement.format(callbackSource = self.callbackSource,
                                  globj = self.globj,
                                  parentId = parentId,
                                  )
        #printTree(rootElement)
        fullMessage = fixHtml(fullMessage)

        shortMessage = None
        linesTolerance = 2
        symbolsTolerance = 200
        if len(fullMessage) > maxLen or len(rootElement.children) > maxLines:
            if len(rootElement.children) > maxLines + linesTolerance:
                rootElement.children = rootElement.children[:maxLines]

            shortMessage = rootElement.format(callbackSource = self.callbackSource,
                                      globj = self.globj,
                                      parentId = parentId,
                                      codeLineNumbers = None
                                      )

            if len(shortMessage) > maxLen:
                cuttedMessage = cutHtml(shortMessage, maxLen)
                if cuttedMessage:
                    shortMessage = cuttedMessage

        if shortMessage:
            if abs(len(fullMessage) - len(shortMessage)) < symbolsTolerance:
                shortMessage = None
            else:
                shortMessage = fixHtml(shortMessage)
        #print fullMessage
        #print shortMessage
        return (fullMessage, shortMessage)
