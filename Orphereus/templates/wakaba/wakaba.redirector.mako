%if c.proceedRedirect:
<script type="text/javascript">
function redirect() {
    var destination = "${h.url_for('boardBase', board = c.currentURL, frameTarget = c.frameTargetToRedir or g.OPT.defaultBoard)}";
%if c.frameEnabled:
    try
    {
      parent.top.list.location.reload(true);
      parent.top.board.window.location=destination;
    } catch(err) //frame not present
    {}
    document.location=destination;
%else:
    try
    {
        parent.top.location=destination;
    } catch(err) //frame not present
    {}
%endif
}
redirect();
</script>

<meta http-equiv="Refresh" content="0; URL=${h.url_for('boardBase', board = c.currentURL, frameTarget = c.frameTargetToRedir or g.OPT.defaultBoard)}" />
%endif
