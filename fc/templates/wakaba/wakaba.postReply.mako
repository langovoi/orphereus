# -*- coding: utf-8 -*-
<%page args="thread, post"/>

<table id="quickReplyNode${post.id}">
    <tbody>
        <tr>
            <td class="doubledash">&gt;&gt;</td>
            <td class="reply" id="reply${post.id}">
                <a name="i${post.id}"></a>
                <label>
                    &nbsp;<a href="javascript:void(0)" onclick="showDeleteBoxes()"><img src='${g.OPT.staticPathWeb}images/delete.gif' border=0 alt='x' title='Del'></a>
                    <div style="display:none" class="delete">
                    %if post.uidNumber == c.uidNumber or c.enableAllPostDeletion:
                        <input type="checkbox" name="delete-${post.id}" value="${post.id}" />
                    %endif                              
                    %if c.isAdmin:
                        <a href="/holySynod/manageUsers/editAttempt/${post.id}">[User]</a>     
                    %endif
                    </div>
                    %if post.sage:
                        <img src='${g.OPT.staticPathWeb}images/sage.png'>
                    %endif
                    <span class="replytitle">${post.title}</span>
                     ${h.modTime(post, c.userInst, g.OPT.secureTime)}
                </label>
                <span class="reflink">
                    %if c.board:
                        <a href="/${thread.id}#i${post.id}" ${c.canPost and """onClick="doQuickReplyForm(event,%s,%s)" """ % (thread.id,post.id) or ""}>#${g.OPT.secondaryIndex and post.secondaryIndex or post.id}</a>
                    %else:
                        <a href="javascript:insert('&gt;&gt;${post.id}')" ${c.canPost and """onClick="doQuickReplyForm(event,%s,%s)" """ % (thread.id,post.id) or ""}>#${g.OPT.secondaryIndex and post.secondaryIndex or post.id}</a>
                    %endif 
                    %if c.canPost and post.file and post.file.width:
                        [<a href="/${post.id}/oekakiDraw">Draw</a>]
                    %endif                                                      
                </span>
                &nbsp;  
                %if post.file:
                    <br /><span class="filesize">${_('File:')}     

                    <a target="_blank" href="${g.OPT.filesPathWeb + h.modLink(post.file.path, c.userInst.secid(), g.OPT.secureLinks)}">${h.modLink(post.file.path, c.userInst.secid(), g.OPT.secureLinks)}</a> 
                    (<em>${'%.2f' % (post.file.size / 1024.0)} Kbytes, ${post.file.width}x${post.file.height}</em>)</span>
                    <span class="thumbnailmsg">${_('This is resized copy. Click it to view original image')}</span><br />
                    <a target="_blank" href="${g.OPT.filesPathWeb + h.modLink(post.file.path, c.userInst.secid(), g.OPT.secureLinks)}">
                    %if post.spoiler:
                        <img src="${g.OPT.staticPathWeb}images/spoiler.png" class="thumb"/>
                    %elif not '..' in post.file.thumpath:                                     
                        <img src="${g.OPT.filesPathWeb + h.modLink(post.file.thumpath, c.userInst.secid(), g.OPT.secureLinks)}" width="${post.file.thwidth}" height="${post.file.thheight}" class="thumb" />
                    %else:  
                        <img src="${g.OPT.filesPathWeb + post.file.thumpath}" width="${post.file.thwidth}" height="${post.file.thheight}" class="thumb" />                                
                    %endif 
                    </a>
                    %elif post.picid == -1:
                        <span class="thumbnailmsg">${_('Picture was removed by user or administrator')}</span><br/>
                        <img src='${g.OPT.staticPathWeb}images/picDeleted.png' class="thumb">                                    
                    %endif
                <blockquote class="postbody" id="postBQId${post.id}">
                    %if (c.count > 1) and post.messageShort and c.userInst.hideLongComments():
                        ${h.modMessage(post.messageShort, c.userInst, g.OPT.secureText)}
                        <br />
                        ${_('Comment is too long.')} <a href="/${thread.id}#i${post.id}"' onClick="getFullText(event,${thread.id},${post.id});" class="expandPost">${_('Full version')}</a>
                    %else:
                        ${h.modMessage(post.message, c.userInst, g.OPT.secureText)}
                    %endif                            
                </blockquote> 
            </td>
        </tr>
    </tbody>
</table>
