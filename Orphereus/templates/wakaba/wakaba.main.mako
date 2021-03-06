# -*- coding: utf-8 -*-
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>

<title> \
${c.title} \
%if c.boardName:
&mdash; ${c.boardName} \
%if c.page and isinstance(c.page, int):
  (${c.page}) \
%endif
%endif
</title>

<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
<meta name="robots" content="noarchive" />
<link rel="shortcut icon" type="image/x-icon" href="${g.OPT.staticPathWeb+g.OPT.favicon}" />
<link rel="icon" type="image/x-icon" href="${g.OPT.staticPathWeb+g.OPT.favicon}" />
<link id="baseCSS" rel="stylesheet" type="text/css" href="${h.staticFile(c.userInst.style + ".css")}" title="${c.userInst.style}" />
<link id="hlCSS" rel="stylesheet" type="text/css" href="${h.staticFile("highlight.css")}" />
<link id="commonCSS" rel="stylesheet" type="text/css" href="${h.staticFile("common.css")}" />

%for jsFile in c.jsFiles:
<script type="text/javascript" src="${h.staticFile(jsFile)}"></script>
%endfor

${h.headCallback(c)}

<%include file="wakaba.redirector.mako" />
</head>

<body>
<%include file="wakaba.jsTest.mako" />

%if not c.suppressMenu:
  %if g.OPT.useZMenu:
    <%include file="wakaba.menu-zero.mako" />
  %else:
    <%include file="wakaba.menuTop.mako" args="menuId='topMenu', menuSource=c.builtMenus" />
  %endif
%endif

%if not c.disableLogo:
<%include file="wakaba.logo.mako" />
%endif

%if not (c.disableLogo and c.suppressMenu):
<hr />
%endif

${self.body()}

%if not c.suppressMenu and not g.OPT.useZMenu:
    <%include file="wakaba.menuTop.mako" args="menuId='topMenu', menuSource=c.builtMenus, bottomMenu = True" />
%endif

%if not c.suppressFooter:
<%include file="wakaba.footer.mako" />
%endif
</body>
</html>
