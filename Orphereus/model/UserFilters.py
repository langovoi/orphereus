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

import sqlalchemy as sa
from sqlalchemy import orm

from Orphereus.model import meta
import datetime

import logging
log = logging.getLogger(__name__)

from Orphereus.model import meta

def t_userfilters_init(dialectProps):
    return sa.Table("userFilters", meta.metadata,
            sa.Column("id"        , sa.types.Integer    , sa.Sequence('userFilters_id_seq'), primary_key = True),
            sa.Column("uidNumber" , sa.types.Integer    , sa.ForeignKey('user.uidNumber'), index = True),
            sa.Column("filter"    , sa.types.Unicode(meta.dialectProps['userFilterLengthLimit']), nullable = False)
            )

class UserFilters(object):
    def __init__(self, uidNumber, filter):
        self.uidNumber = uidNumber
        maxLen = meta.dialectProps['userFilterLengthLimit']
        self.filter = filter[:maxLen]
