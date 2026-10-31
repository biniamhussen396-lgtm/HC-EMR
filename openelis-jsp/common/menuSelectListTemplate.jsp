<%@ page language="java"
	contentType="text/html; charset=utf-8"
	import="org.apache.struts.util.RequestUtils,org.apache.struts.action.*,org.apache.struts.Globals,java.util.Iterator,javax.servlet.jsp.JspException"
	import="us.mn.state.health.lims.common.action.IActionConstants"
	import="us.mn.state.health.lims.common.util.StringUtil"
	import="us.mn.state.health.lims.common.util.resources.ResourceLocator"
 %>
<%@ taglib uri="/WEB-INF/struts-html.tld" prefix="html" %>
<%@ taglib uri="/WEB-INF/struts-bean.tld" prefix="bean" %>
<%@ taglib uri="/WEB-INF/struts-tiles.tld" prefix="tiles" %>
<%@ taglib uri="/WEB-INF/struts-logic.tld" prefix="logic" %>

<%--action is set in BaseAction--%>

 <%
 String _actionKey = (String)request.getAttribute(IActionConstants.ACTION_KEY);
 String _formName = (String)request.getAttribute(IActionConstants.FORM_NAME);

 // Fix: When action fails (NPE), BaseMenuAction forwards to /MasterListsPage.do which
 // overwrites Globals.MAPPING_KEY with the MasterListsPage mapping (mainForm).
 // The menuDefinition attribute is set BEFORE the forward, so use it to derive the
 // correct form name and action path for the current menu.
 String _menuDef = (String)request.getAttribute("menuDefinition");
 if (_menuDef != null && _menuDef.length() > 0 && !_menuDef.equals("default")) {
     // menuDefinition like "AnalyzerTestNameMenuDefinition" → form = "analyzerTestNameMenuForm"
     // Strip "Definition" suffix → "AnalyzerTestNameMenu"
     String _menuBase = _menuDef;
     if (_menuBase.endsWith("Definition")) {
         _menuBase = _menuBase.substring(0, _menuBase.length() - 10);
     }
     _formName = _menuBase.substring(0, 1).toLowerCase() + _menuBase.substring(1) + "Form";
     _actionKey = "/" + _menuBase;
     request.setAttribute(IActionConstants.FORM_NAME, _formName);
     request.setAttribute(IActionConstants.ACTION_KEY, _actionKey);
 } else {
     // Fallback: use ActionMapping if menuDefinition is not available
     ActionMapping _mapping = (ActionMapping) request.getAttribute(Globals.MAPPING_KEY);
     if (_mapping != null) {
         String _mappingFormName = _mapping.getName();
         String _mappingPath = _mapping.getPath();
         if (_mappingFormName != null && _mappingFormName.length() > 0) {
             _formName = _mappingFormName;
             request.setAttribute(IActionConstants.FORM_NAME, _formName);
         }
         if (_mappingPath != null && _mappingPath.length() > 0) {
             _actionKey = _mappingPath;
             request.setAttribute(IActionConstants.ACTION_KEY, _actionKey);
         }
     }
 }

 // Fallback: derive action from form name if action is missing
 if (_actionKey == null && _formName != null && _formName.length() > 4) {
     _actionKey = "/" + _formName.substring(0, 1).toUpperCase() + _formName.substring(1, _formName.length() - 4);
     request.setAttribute(IActionConstants.ACTION_KEY, _actionKey);
 }
 if (_actionKey != null) {
 %>
 <form name='<%= _formName %>' action='<%= _actionKey %>' onsubmit="return submitForm(this);" method="POST">
 <% } %>

	<table cellpadding="0" cellspacing="1" width="100%" height="100%" border="0">
	
			<tr valign="top">
				<td><tiles:insert attribute="preSelectionHeader"/></td>
			</tr>
			<tr valign="top">
				<td>
					<tiles:insert attribute="header"/>
				</td>
			</tr>
			<tr valign="top">
				<td>
					<tiles:insert attribute="body"/>
				</td>
			</tr>
			<tr valign="bottom">
				<td>
					<tiles:insert attribute="footer"/>
				</td>
			</tr>

	</table>
<% if (_actionKey != null) { %>
</form>
<% } %>
