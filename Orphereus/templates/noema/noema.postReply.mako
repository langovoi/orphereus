# -*- coding: utf-8 -*-
<%page args="thread, post"/>

<div class="post-wrapper" id="postWrapper${post.id}">
    <div
            %if g.OPT.memcachedPosts and not (c.userInst.isAdmin()):
            class="post"
            %else:
                %if not (c.userInst.hlOwnPosts and c.userInst.ownPost(post)):
                class="post"
                %else:
                class="post own"
                %endif
            %endif
            id="i${post.id}"
            data-id="${post.id}">
        <div class="post-head">
            <span class="post-control">
                <a class="pseudo-link" title="Управление постом" data-id="${post.id}">×</a>
                %if c.userInst.ownPost(post) or (thread.selfModeratable() and c.userInst.ownPost(thread)) or c.enableAllPostDeletion:
                <input type="checkbox" class="delete" 
                    name="delete-${post.id}" value="${post.id}">
                %endif
            </span>
            %if post.sage:
            <img src="${g.OPT.staticPathWeb}images/sage.png" class="sage" alt="sage" title="sage">
            %endif
            <a class="post-id" href="${h.postUrl(thread.id, post.id)}">#${g.OPT.secondaryIndex and post.secondaryIndex or post.id}</a>
            <span class="post-date"> ${h.tsFormat(post.date)}</span>
            
            %if post.attachments and (len(post.attachments) == 1):
            %for attachment in post.attachments:
            <span class="post-file-info">
                Файл:
                <a href="${g.OPT.filesPathWeb + h.modLink(attachment.attachedFile.path, c.userInst.secid())}">${attachment.attachedFile.path.split('.')[-1]}</a>,
                ${'%.2f' % (attachment.attachedFile.size / 1024.0)} К
                %if attachment.attachedFile.width and attachment.attachedFile.height:
                — ${attachment.attachedFile.width}×${attachment.attachedFile.height}
                %endif
            </span>
            %endfor
            %endif
            <!--span class="post-action"><a href="#/ololo/12">рисовать</a></span-->
        </div>
        
        %if post.attachments:
        <%include file="noema.fileBlock.mako" args="post=post,opPost=False,searchMode=None,newsMode=None" />
        %endif
        
        <div class="post-text">
            %if post.title:
            <h2>${post.title}</h2>
            %endif
            <div class="real-post-text">
                %if (c.count > 1) and post.messageShort and c.userInst.hideLongComments:
                ${post.messageShort}
                <a class="post-cut" href="${h.postUrl(thread.id, post.id)}" data-id="${post.id}">дальше →</a>
                %else:
                ${post.message}
                %endif
                %if post.messageInfo:
                <div>${post.messageInfo}</div>
                %endif
                %if post.attachments and len(post.attachments) == 1:
                <%include file="noema.fileInfoSingle.mako" args="attachment=post.attachments[0]" />
                %endif
            </div>
        </div>
    </div>
</div>
