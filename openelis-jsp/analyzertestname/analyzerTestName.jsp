<%@ page language="java" contentType="text/html; charset=utf-8"
	import="java.util.Date,
	us.mn.state.health.lims.common.action.IActionConstants,
	us.mn.state.health.lims.common.util.StringUtil,
	us.mn.state.health.lims.userrole.action.UserRoleAction"%>

<%@ taglib uri="/tags/struts-bean" prefix="bean"%>
<%@ taglib uri="/tags/struts-html" prefix="html"%>
<%@ taglib uri="/tags/struts-logic" prefix="logic"%>
<%@ taglib uri="/tags/labdev-view" prefix="app"%>

<bean:define id="formName" value='<%=(String) request.getAttribute(IActionConstants.FORM_NAME)%>' />

<%!String allowEdits = "true";%>

<%
	if (request.getAttribute(IActionConstants.ALLOW_EDITS_KEY) != null) {
		allowEdits = (String) request.getAttribute(IActionConstants.ALLOW_EDITS_KEY);
	}
%>

<script language="JavaScript1.2">
function validateForm(form) {

	if( $("analyzerId").selectedIndex == 0 ||
	    $("analyzerTestNameId").value == null ||
	    $("testId").selectedIndex == 0 ){
	    		alert('<%=StringUtil.getMessageForKey("error.all.required") %>');
	    		return false;
	    }

    return true;
}

function prePopulateFromId() {
    var urlParams = window.location.search.substring(1);
    var params = urlParams.split('&');
    for (var i = 0; i < params.length; i++) {
        var pair = params[i].split('=');
        if (pair[0] === 'ID' && pair[1] && pair[1] !== '0') {
            var decoded = decodeURIComponent(pair[1]);
            var sepIdx = decoded.indexOf('-');
            if (sepIdx > 0) {
                var analyzerName = decoded.substring(0, sepIdx);
                var testFieldName = decoded.substring(sepIdx + 1);
                var analyzerSelect = document.getElementById('analyzerId');
                if (analyzerSelect) {
                    for (var j = 1; j < analyzerSelect.options.length; j++) {
                        if (analyzerSelect.options[j].text === analyzerName) {
                            analyzerSelect.selectedIndex = j;
                            break;
                        }
                    }
                }
                var testField = document.getElementById('analyzerTestNameId');
                if (testField) {
                    testField.value = testFieldName;
                }
            }
        }
    }
}
window.onload = function() { prePopulateFromId(); };
</script>

<table width="60%">
	<tr>
		<td class="label" width="20%">
			<bean:message key="analyzer.label" />
			:
			<span class="requiredlabel">*</span>
		</td>
		<td width="80%">
			<html:select name="<%=formName%>" property="analyzerId" styleId="analyzerId" >
				<html:option value="0">&nbsp;</html:option>
				<html:optionsCollection name="<%=formName%>" property="analyzerList" label="name" value="id"/>
			</html:select>

		</td>
	</tr>
	<tr>
		<td class="label" >
		<bean:message key="analyzer.test.name" />
			:
			<span class="requiredlabel">*</span>
		</td>
		<td >
			<html:text name='<%=formName%>' property="analyzerTestName" styleId="analyzerTestNameId" />
		</td>
	</tr>
	<tr>
		<td class="label" >
		<bean:message key="analyzer.test.actual.name" />
			:
			<span class="requiredlabel">*</span>
		</td>
		<td >
			<html:select name="<%=formName%>" property="testId" styleId="testId" >
				<html:option value="0">&nbsp;</html:option>
				<html:optionsCollection name="<%=formName%>" property="testList" label="name" value="id"/>
			</html:select>
		</td>
	</tr>
	<tr>
		<td>
			&nbsp;
		</td>
	</tr>
</table>


