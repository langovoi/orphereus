# -*- coding: utf-8 -*-
<%inherit file="wakaba.main.mako" />
<div class="theader">${_('Profile')}</div>

<form id="postform" action="/userProfile/" method="post">
    <div class="postarea">
        <table>
            <tbody>
                %if c.profileChanged:
                    <tr>
                        <td colspan='2' style="text-align: center;"><span class="theader">${_('Profile was updated.')}</span></td>
                    </tr>                    
                %endif   
                <tr>
                    <td colspan='2' style="text-align: center; font-weight: bold;">${_('Security')}</td>
                </tr>                   
                <tr id="truid">
                    <td class="postblock">${_('UID')}</td>
                    <td><input value='${c.userInst.uid()}' readonly></td>
                </tr>
                <tr>
                    <td colspan='2' style="font-size: 50%;">${_("Leave this fields empty if you don't wish to change your security code and UID:")}</td>
                </tr>                                   
                <tr>
                    <td class="postblock">${_('New Security Code')}</td>
                    <td><input name='key' value=''></td>
                </tr>                  
                <tr>
                    <td class="postblock">${_('Repeat Security Code')}</td>
                    <td><input name='key2' value=''></td>
                </tr>  
                <tr>
                    <td colspan='2' style="text-align: center; font-weight: bold;">${_('Customization')}</td>
                </tr>                   
                <tr id="trtpp">
                    <td class="postblock">${_('Threads per page')}</td>
                    <td><input name='threadsPerPage' value='${c.userInst.threadsPerPage()}'></td>
                </tr>
                <tr id="trppt">
                    <td class="postblock">${_('Replies per thread')}</td>
                    <td><input name='repliesPerThread' value='${c.userInst.repliesPerThread()}'></td>
                </tr>
                <tr>
                    <td class="postblock">${_('Hide long comments')}</td>
                    <td><input type="checkbox" name='hideLongComments' ${c.userInst.hideLongComments() and "checked" or ""}></td>
                </tr>                
                <tr>
                    <td class="postblock">${_('Home filter exclusions')}</td>
                    <td><input name='homeExclude' value='${c.homeExclude}'></td>
                </tr>                
                <tr id="trtempl">
                    <td class="postblock">${_('Template')}</td>
                    <td>
                        <select name name='template'>
                            <option>${c.userInst.template()}</option>
                            %for t in c.templates:
                                %if t != c.userInst.template():
                                    <option>${t}</option>
                                %endif 
                            %endfor
                        </select>
                    </td>
                </tr>
                <tr id="trstyle">
                    <td class="postblock">${_('Style')}</td>
                    <td>
                        <select name='style'>
                            <option>${c.userInst.style()}</option>
                            %for s in c.styles:
                                %if s != c.userInst.style():
                                    <option>${s}</option>
                                %endif
                            %endfor
                        </select>                            
                    </td>
                </tr>                              
                <tr>
                    <td colspan='2'><input name='update' type='submit' value='${_('Update')}'></td>
                </tr>
                <tr>
                    <td colspan='2' style="text-align: center; font-weight: bold;">${_('User filters')}</td>
                </tr>                
                %for f in c.userInst.filters():
                <tr id='filterId${f.id}'>
                    <td class="postblock">[<a href='' onClick="userFiltersEdit(event,${f.id});">Edit</a>] [<a href='' onClick="userFiltersDelete(event,${f.id});">Del</a>]</td>
                    <td><input id='filterId${f.id}Input' name='filterId${f.id}' value='${f.filter}'></td>
                </tr>
                %endfor
                <tr id='newFilterTR'>
                    <td class="postblock">${_('New filter')}</td>
                    <td><input id='newFilterInput' name='newFilter' value=''></td>
                </tr>  
                <tr>
                    <td colspan='2'><input name='update' type='button' value='${_('Add')}' onClick="userFiltersAdd(event)"></td>
                </tr>
            </tbody>
        </table>
    </div>
</form>