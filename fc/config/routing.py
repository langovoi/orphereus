"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from pylons import config
from routes import Mapper
from pylons import config

def make_map():
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('error/:action/:id', controller='error')

    # CUSTOM ROUTES HERE
    # debug route
    if config['core.devMode'] == 'true':
        map.connect('/uaInfo', controller='fcp', action='uaInfo')

    # Special routes
    #map.connect('', controller='fcc', action='GetOverview')
    map.connect('authorize', '/authorize', controller='fcp', action='authorize', url='')
    map.connect('captcha', '/captcha/:cid', controller='fcp', action='captchaPic', cid=0)
    map.connect('logout', '/logout', controller='fcp', action='logout', url='')
    map.connect('authorizeToUrl', '/*url/authorize', controller='fcp', action='authorize', url='')
    map.connect('register', '/register/:invite', controller='fcp', action='register')
    map.connect('search', '/search/:text/:page_dummy/:page', controller='fcc', action='search', text='', page=0, page_dummy='page', requirements=dict(page='\d+'))
    #map.connect('/search/:text/page/:page', controller='fcc', action='search', text='', page=0, requirements=dict(page='\d+'))
    map.connect('/youAreBanned', controller='fcp', action='banned')
    #map.connect('/Join', controller='fcp', action='showStatic', page = 'Join')

    # Oekaki
    map.connect('/:url/oekakiDraw', controller='fcc', action='oekakiDraw', url='', selfy='-selfy', anim='-anim', tool='shiNormal')
    map.connect('/:url/oekakiDraw/:selfy/:anim/:tool', controller='fcc', action='oekakiDraw', url='')
    map.connect('/:url/oekakiSave/:tempid', controller='fcp', action='oekakiSave', url='',requirements=dict(tempid='\d+'))
    map.connect('/viewAnimation/:source', controller='fcc', action='viewAnimation', requirements=dict(source='\d+'))

    # User subsystem
    map.connect('userProfile', '/userProfile', controller='fcc', action='showProfile')
    map.connect('viewLog', '/viewLog/:page_dummy/:page', controller='fcc', action='viewLog', page_dummy='page', page=0, requirements=dict(page='\d+'))
    #map.connect('viewLogPage', '/viewLog/page/:page', controller='fcc', action='viewLog', page=0, requirements=dict(page='\d+'))
    #map.connect('/userProfile/messages', controller='fcc', action='showMessages')

    # Admin subsystem
    map.connect('holySynod', '/holySynod', controller='fca', action='index')
    map.connect('/holySynod/makeInvite', controller='fca', action='makeInvite')
    map.connect('/holySynod/manageSettings', controller='fca', action='manageSettings')
    map.connect('/holySynod/manageExtensions', controller='fca', action='manageExtensions')
    map.connect('/holySynod/manageExtensions/edit/:name', controller='fca', name='', action='editExtension')
    map.connect('/holySynod/manageBoards', controller='fca', action='manageBoards')
    map.connect('/holySynod/manageBoards/edit/:tag', controller='fca', tag='', action='editBoard')
    map.connect('/holySynod/manageUsers', controller='fca', action='manageUsers')
    map.connect('/holySynod/manageUsers/editAttempt/:pid', controller='fca', action='editUserAttempt', requirements=dict(pid='\d+'))
    map.connect('/holySynod/manageUsers/editUserByPost/:pid', controller='fca', action='editUserByPost', requirements=dict(pid='\d+'))
    map.connect('/holySynod/manageUsers/edit/:uid', controller='fca', action='editUser', requirements=dict(uid='\d+'))
    map.connect('/holySynod/viewLog', controller='fca', action='viewLog', page=0, requirements=dict(page='\d+'))
    map.connect('/holySynod/viewLog/page/:page', controller='fca', action='viewLog', page=0, requirements=dict(page='\d+'))
    map.connect('/holySynod/manageMappings/:act/:id/:tagid', controller='fca', action='manageMappings', act='show', id=0, tagid=0, requirements=dict(id='\d+', tagid='\d+'))

    # Maintenance
    map.connect('/holySynod/service/:actid/:secid', controller='fcm', actid='', secid='', action='mtnAction')

    # AJAX
    map.connect('/ajax/hideThread/:post/*redirect', controller='fcajax', action='hideThread', requirements=dict(post='\d+'))
    map.connect('/ajax/showThread/:post/:redirect', controller='fcajax', action='showThread', redirect='', requirements=dict(post='\d+'))
    map.connect('/ajax/getPost/:post', controller='fcajax', action='getPost', requirements=dict(post='\d+'))
    map.connect('/ajax/getRenderedPost/:post', controller='fcajax', action='getRenderedPost', requirements=dict(post='\d+'))
    map.connect('/ajax/getRenderedReplies/:thread', controller='fcajax', action='getRenderedReplies', requirements=dict(thread='\d+'))
    map.connect('/ajax/editUserFilter/:fid/:filter', controller='fcajax', action='editUserFilter', requirements=dict(fid='\d+'))
    map.connect('/ajax/deleteUserFilter/:fid', controller='fcajax', action='deleteUserFilter', requirements=dict(fid='\d+'))
    map.connect('/ajax/addUserFilter/:filter', controller='fcajax', action='addUserFilter')
    map.connect('/ajax/getRepliesCountForThread/:post', controller='fcajax', action='getRepliesCountForThread', requirements=dict(post='\d+'))
    map.connect('/ajax/getRepliesIds/:post', controller='fcajax', action='getRepliesIds', requirements=dict(post='\d+'))
    map.connect('/ajax/getUserSettings', controller='fcajax', action='getUserSettings')
    map.connect('/ajax/getUploadsPath', controller='fcajax', action='getUploadsPath')
    map.connect('/ajax/checkCaptcha/:id/:text', controller='fcajax', action='checkCaptcha', text='', requirements=dict(id='\d+'))

    # Threads
    map.connect('/:post', controller='fcc', action='PostReply', conditions=dict(method=['POST']), requirements=dict(post='\d+'))
    map.connect('/:board/delete', controller='fcc', action='DeletePost',conditions=dict(method=['POST']))
    map.connect('/:post/anonymize', controller='fcc', action='Anonimyze', requirements=dict(post='\d+'))
    map.connect('/:post/:tempid', controller='fcc', action='GetThread', tempid=0, requirements=dict(post='\d+',tempid='\d+'))
    map.connect('/:board', controller='fcc', action='PostThread',conditions=dict(method=['POST']))

    # Generic filter
    map.connect('board', '/:board/:tempid', controller='fcc', action='GetBoard', board = '!', tempid=0, requirements=dict(tempid='\d+'))
    map.connect('boardPage', '/:board/page/:page', controller='fcc', action='GetBoard', tempid=0, page=0, requirements=dict(page='\d+'))

    map.connect('/static/:page', controller='fcc', action='showStatic', page = 'Rules')

    # traps for bots
    map.connect('botTrap1', '/ajax/stat/:confirm', controller='fcc', action='selfBan', confirm = '')
    map.connect('botTrap2','/holySynod/stat/:confirm', controller='fcc', action='selfBan', confirm = '')

    map.connect('*url', controller='fcp', action='UnknownAction')

    return map
