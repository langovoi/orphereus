import pickle
from fc.lib.base import *
from fc.lib.miscUtils import *
from fc.model import UserOptions

class FakeUser(object):
    def __init__(self):
        self.__valid = False
        self.Anonymous = False

        if g.OPT.allowAnonymous:
            self.__valid = True
            self.Anonymous = True
            self.uidNumber = -1
            self.uid = "Anonymous"
            self.filters = ()

            self.__user = empty()
            self.__user.uidNumber = -1
            self.__user.filters = ()

            self.__user.options = empty()
            UserOptions.initDefaultOptions(self.__user.options, g.OPT)

    def isValid(self):
        return self.__valid

    def setUid(self, value=None):
        return self.__user.uid

    def defaultGoto(self, value = None):
        return self.__user.options.defaultGoto

    def isBanned(self):
        return False

    def isAdmin(self):
        return False

    def secid(self):
        return 0

    def hideLongComments(self, value=None):
        return self.__user.options.hideLongComments

    def mixOldThreads(self, value=None):
        return self.__user.options.mixOldThreads

    def useAjax(self, value=None):
        return self.__user.options.useAjax

    def homeExclude(self, value = None):
        return pickle.loads(self.__user.options.homeExclude)

    def hideThreads(self, value = None):
        return pickle.loads(self.__user.options.hideThreads)

    def threadsPerPage(self, value = False):
        return self.__user.options.threadsPerPage

    def repliesPerThread(self, value = False):
        return self.__user.options.repliesPerThread

    def style(self, value = False):
        return self.__user.options.style

    def template(self, value = False):
        return self.__user.options.template

    def canDeleteAllPosts(self):
        return False

    def canMakeInvite(self):
        return False

    def canChangeRights(self):
        return False

    def bantime(self):
        return 0

    def banreason(self):
        return u''

    def optionsDump(self):
        return UserOptions.optionsDump(self.options)

    def canChangeSettings(self):
        return False

    def canManageBoards(self):
        return False

    def canManageUsers(self):
        return False

    def canManageExtensions(self):
        return False

    def canManageMappings(self):
        return False

    def canRunMaintenance(self):
        return False

    def expandImages(self):
        return self.__user.options.expandImages

    def maxExpandWidth(self):
        return self.__user.options.maxExpandWidth

    def maxExpandHeight(self):
        return self.__user.options.maxExpandHeight
