%if c.boardlist:
<div class="adminbar">
    [
    <a href="/~/" title="${_('Overview')}">/~/</a>
    <a href="/@/" title="${_('Related threads')}">/@/</a>
    <a href="/!/" title="${_('Home')}">/!/</a>    
    ]    
    %for section in c.boardlist:
        [
        %for board in section:
            <a href="/${board.tag}/" title="${board.comment}"><b>/${board.tag}/</b></a>
        %endfor
        ]
    %endfor
	[<a href="/userProfile/">${_('Profile')}</a>]
    %if c.userInst.isAdmin():
        [<a href="/holySynod/">${_('Holy Synod')}</a>]
    %endif 
    %if c.settingsMap['usersCanViewLogs'].value == 'true':
        [<a href="/viewLog/">${_('Logs')}</a>]
    %endif     
    [<a href="/logout/">${_('Logout')}</a>]
    %if c.userInst.filters():
        <br />
        [
        %for f in c.userInst.filters():
            <a href="/${f.filter}/">/${f.filter}/</a>
        %endfor
        ]
    %endif
</div>
%endif
