import sys
import os 

hashSecret = 'paranoia' # We will hash it by sha512, so no need to have it huge
uploadPath = os.path.join(sys.path[0],'fc/public/uploads/')
uploadPathWeb = '/uploads/'
markupFile = os.path.join(sys.path[0],'wakabaparse/mark.def')

settingsDef = {
    "title"         : "ANOMA.Ch",
    "invisibleBump" : 'true',
    "maxTagsCount"  : '5',
    "maxTagLen"     : '6',
    "disabledTags"  : 'logout,authorize,register,youAreBanned,userProfile,holySynod',
    "adminOnlyTags" : 'synod,logs'
}

LOG_EVENT_SECURITY_IP   = 0x00000001
LOG_EVENT_INVITE        = 0x00010001
LOG_EVENT_BOARD_EDIT    = 0x00020001
LOG_EVENT_BOARD_DELETE  = 0x00020002
LOG_EVENT_USER_EDIT     = 0x00030001
LOG_EVENT_USER_DELETE   = 0x00030002
LOG_EVENT_USER_ACCESS   = 0x00030003
LOG_EVENT_USER_BAN      = 0x00030004
LOG_EVENT_USER_UNBAN    = 0x00030005
LOG_EVENT_USER_GETUID   = 0x00030006
LOG_EVENT_SETTINGS_EDIT = 0x00040001
LOG_EVENT_POSTS_DELETE  = 0x00050001
LOG_EVENT_EXTENSION_EDIT= 0x00060001