# -*- coding: utf-8 -*-
<%inherit file="wakaba.main.mako" />

%if c.page=='rules' or c.page=='markup' or c.page=='rulesFull':
    <%include file="wakaba.${c.page}.mako" />
%endif

<br clear="all" />