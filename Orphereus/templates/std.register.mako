# -*- coding: utf-8 -*-
<%inherit file="std.main.mako" />

<div class="postarea">
<form id="postform" action="${h.url_for('register', invite='doesntmatteranymore')}" method="post">
<h2>${_('New UID')}</h2>
%if c.message:
<h3 class="errorMessage">
    ${c.message}
</h3>
%endif

<p><i>
${_('Now you can enter your personal security code.')}
%if not g.OPT.allowRegistration:
    <br/>
    ${_("Warning: you can't use this link twice.")}
    <br/>
    ${_("If you close browser now you'll loss your ability to join us.")}
    <br/>
%endif
%if g.OPT.setReadonlyToRegistered or c.roInvite:
    <br/>
    ${_("After registration you will be in read-only mode!")}
    <br/>
%endif
</i></p>

<span class="postblock">${_('Enter your security code')}</span>
<p><input name="key" type="password" size="60" /></p>
<span class="postblock">${_('Re-enter security code')}</span>
<p><input name="key2" type="password" size="60" /></p>
<i>${_('Security code should be at least %d symbols') % g.OPT.minPassLength}</i>

%if c.captcha:
    <br/>
    <span class="postblock">${_('Enter captcha')}</span>
    <div><img src="${h.url_for('captcha', cid=c.captcha.id)}" alt="Captcha" /></div>
    <p><input name="captcha" type="text" size="60" /></p>
%endif

<p><input type="submit" value="${_('OK')}" /></p>
</form>
</div>
