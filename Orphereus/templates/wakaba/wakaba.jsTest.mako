<script type="text/javascript">
var CSSRules = function() {
 
 var headElement = document.getElementsByTagName("head")[0],
  styleElement = document.createElement("style");
 styleElement.type = "text/css";
 headElement.appendChild(styleElement);
 
 // memoize the browser-dependent add function
 var add = function() {
  // IE doesn't allow you to append text nodes to <style> elements
  if (styleElement.styleSheet) {
   return function(selector, rule) {
    if (styleElement.styleSheet.cssText == '') {
     styleElement.styleSheet.cssText = '';
    }
    styleElement.styleSheet.cssText += selector + " { " + rule + " }";
   }
  } else {
   return function(selector, rule) {
    styleElement.appendChild(document.createTextNode(selector + " { " + rule + " }"));
   }
  }
 }();
 
 return {
  add : add
 }
}();
 
CSSRules.add('#systemAlert', 'display: none');
</script>

<div id="systemAlert">
<div id="systemAlertText" style="border: 1px solid #FF0000; background-color: #EEAAAA; color: #880000; position: fixed; left: 0px; top: 0px; margin-left: 0; padding: 0; width: 100%;">
${_("<b>Warning</b>: It's strongly recommended to enable JavaScript for this site!")} 
</div>
<div id="systemAlertMargin">&nbsp;</div>
</div>

<script type="text/javascript">
 if (!document.cookie) {
     var rnd = Math.random();
     document.cookie = rnd;
     if (!document.cookie != rnd)
     {
     $("#systemAlertText").html("${_("<b>Warning</b>: It's strongly recommended to turn cookies on for this site.")}");
        $("#systemAlert").show();
     }
     else
     {
         document.cookie = "";
     }
 }
</script>