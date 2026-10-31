<%@ page language="java"
	contentType="text/html; charset=utf-8"
	import="java.util.Date,
	java.text.SimpleDateFormat,
	us.mn.state.health.lims.common.util.SystemConfiguration,
	us.mn.state.health.lims.common.action.IActionConstants" %>
<%@ page import="us.mn.state.health.lims.common.util.ConfigurationProperties" %>

<%@ taglib uri="/tags/struts-bean" prefix="bean" %>
<%@ taglib uri="/tags/struts-html" prefix="html" %>
<%@ taglib uri="/tags/struts-logic" prefix="logic" %>
<%@ taglib uri="/tags/labdev-view" prefix="app" %>
<bean:define id="formName" value='<%= (String)request.getAttribute(IActionConstants.FORM_NAME) %>' />
<bean:define id="todayOrderListJson" name="<%=formName%>" property="todayOrderList" />
<bean:define id="todaySampleNotCollectedListJson" name="<%=formName%>" property="todaySampleNotCollectedList" />
<bean:define id="backlogSampleNotCollectedListJson" name="<%=formName%>" property="backlogSampleNotCollectedList" />
<bean:define id="backlogOrderListJson" name="<%=formName%>" property="backlogOrderList" />
<bean:define id="showPriorityColumn" name="<%=formName%>" property="isGroupBySample" />

<%!
String path = "";
String basePath = "";
String serverNow = new SimpleDateFormat("yyyy/MM/dd").format(new Date());
Boolean alwaysValidate = ConfigurationProperties.getInstance().isPropertyValueEqual(ConfigurationProperties.Property.ALWAYS_VALIDATE_RESULTS, "true");
Boolean showReferredTestsCount = ConfigurationProperties.getInstance().isPropertyValueEqual(ConfigurationProperties.Property.SHOW_REFERRED_TESTS_COUNT, "true");
Boolean showPatientsDetailsInSampleLabelPrint = ConfigurationProperties.getInstance().isPropertyValueEqual(ConfigurationProperties.Property.SHOW_PATIENT_DETAILS_SAMPLE_LABEL_PRINT, "true");
%>

<%
path = request.getContextPath();
basePath = path + "/";
String selectedLabLocationName = (String) session.getAttribute("selectedLabLocationName");
if (selectedLabLocationName == null) selectedLabLocationName = "";
%>

<link rel="stylesheet" type="text/css" href="<%=basePath%>css/slickgrid/examples.css" />
<link rel="stylesheet" type="text/css" href="<%=basePath%>css/slickgrid/slick.grid.css" />

<script type="text/javascript" src="<%=basePath%>scripts/ui/jquery.event.drag-2.2.js"></script>
<script type="text/javascript" src="<%=basePath%>scripts/ui/jquery.event.drop-2.2.js"></script>
<script type="text/javascript" src="<%=basePath%>scripts/slickgrid/slick.core.js"></script>
<script type="text/javascript" src="<%=basePath%>scripts/slickgrid/slick.formatters.js"></script>
<script type="text/javascript" src="<%=basePath%>scripts/slickgrid/slick.cellrangedecorator.js"></script>
<script type="text/javascript" src="<%=basePath%>scripts/slickgrid/slick.cellrangeselector.js"></script>
<script type="text/javascript" src="<%=basePath%>scripts/slickgrid/slick.cellexternalcopymanager.js"></script>
<script type="text/javascript" src="<%=basePath%>scripts/slickgrid/slick.cellselectionmodel.js"></script>
<script type="text/javascript" src="<%=basePath%>scripts/slickgrid/slick.rowselectionmodel.js"></script>
<script type="text/javascript" src="<%=basePath%>scripts/slickgrid/slick.dataview.js"></script>
<script type="text/javascript" src="<%=basePath%>scripts/slickgrid/slick.grid.js"></script>
<script type="text/javascript" src="<%=basePath%>scripts/slickgrid/slick.editors.js"></script>
<script type="text/javascript" src="<%=basePath%>scripts/slickgrid/merge-sort.js"></script>
<script type="text/javascript" src="<%=basePath%>scripts/dashBoard/orders.js"></script>
<script type="text/javascript" src="<%=basePath%>scripts/dashBoard/createGrid.js"></script>
<script type="text/javascript" src="<%=basePath%>scripts/slickgrid/slick.autotooltips.js"></script>
<script type="text/javascript" src="<%=basePath%>scripts/utils.js"></script>
<script type="text/javascript" src="<%=basePath%>scripts/JsBarcode.all.min.js"></script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden}
body>table>tbody>tr:first-child,body>table>tbody>tr:nth-child(2),body>table>tbody>tr:last-child{display:none!important}
body>table{border:none!important;width:100%!important;height:calc(100vh - 85px)!important;border-collapse:collapse!important;margin:0!important;padding:0!important}
body>table>tbody>tr:nth-child(3)>td{padding:0!important;margin:0!important;vertical-align:top!important;height:100%!important}
.od-body{font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f0f2f5;color:#1a1a2e;line-height:1.5;display:flex;flex-direction:column;height:calc(100vh - 85px);overflow:hidden}
form[name="menuForm"]{position:sticky!important;top:0!important;z-index:50!important;background:#fff!important;flex-shrink:0}

.od-sticky-top{background:#f0f2f5;padding:8px 16px 0;border-bottom:1px solid #e2e8f0;flex-shrink:0}
.od-header{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:8px;flex-wrap:wrap}
.od-header-left{display:flex;align-items:center;gap:8px}
.od-logo{width:32px;height:32px;background:linear-gradient(135deg,#0f766e,#14b8a6);border-radius:7px;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:14px;flex-shrink:0}
.od-title{font-size:16px;font-weight:700;color:#0f172a}
.od-subtitle{font-size:10px;color:#64748b}
.od-header-right{display:flex;align-items:center;gap:5px;flex-wrap:wrap;flex-shrink:0}
.od-location-badge{display:inline-flex;align-items:center;gap:4px;padding:4px 8px;background:linear-gradient(135deg,#0f766e,#14b8a6);color:#fff;border-radius:5px;font-size:10px;font-weight:600;white-space:nowrap}
.od-location-badge svg{width:12px;height:12px}
.od-refresh-btn,.od-customize-btn,.od-nav-btn{display:inline-flex;align-items:center;gap:4px;padding:4px 8px;background:#fff;color:#334155;border:1px solid #e2e8f0;border-radius:5px;font-size:10px;font-weight:500;cursor:pointer;transition:all .15s;white-space:nowrap;flex-shrink:0;height:26px;text-decoration:none}
.od-refresh-btn:hover,.od-customize-btn:hover,.od-nav-btn:hover{background:#f8fafc;border-color:#cbd5e1}
.od-refresh-btn svg,.od-customize-btn svg,.od-nav-btn svg{width:12px;height:12px}
.od-nav-btn.active{background:#1d4ed8;color:#fff;border-color:#1d4ed8}
.od-nav-group{display:flex;gap:0}
.od-nav-group .od-nav-btn{border-radius:0;border-right-width:0}
.od-nav-group .od-nav-btn:first-child{border-radius:5px 0 0 5px}
.od-nav-group .od-nav-btn:last-child{border-radius:0 5px 5px 0;border-right-width:1px}

.od-stats{display:grid;grid-template-columns:repeat(6,1fr);gap:6px;margin-bottom:8px}
.od-stat-card{background:#fff;border-radius:7px;padding:7px 10px;display:flex;align-items:center;gap:8px;box-shadow:0 1px 2px rgba(0,0,0,.04);border:1px solid #f1f5f9;transition:all .15s}
.od-stat-card.od-card-highlight{border-color:#1d4ed8;box-shadow:0 0 0 2px rgba(29,78,216,.12)}
.od-stat-icon{width:28px;height:28px;border-radius:6px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.od-stat-icon svg{width:14px;height:14px}
.od-stat-icon.teal{background:#f0fdfa;color:#0f766e}
.od-stat-icon.blue{background:#eff6ff;color:#1d4ed8}
.od-stat-icon.amber{background:#fffbeb;color:#b45309}
.od-stat-icon.green{background:#f0fdf4;color:#15803d}
.od-stat-icon.purple{background:#faf5ff;color:#7c3aed}
.od-stat-icon.rose{background:#fff1f2;color:#be123c}
.od-stat-label{font-size:9px;color:#64748b;text-transform:uppercase;letter-spacing:.4px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.od-stat-value{font-size:18px;font-weight:700;color:#0f172a;line-height:1}
.od-stat-card.od-card-hidden{display:none!important}

.od-main-content{flex:1;padding:8px 16px;display:flex;flex-direction:column;min-height:0;overflow:hidden}

    .od-section{background:#fff;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,.06);border:1px solid #f1f5f9;flex:1;display:flex;flex-direction:column;min-height:0;overflow:hidden}
.od-section-body{display:flex;flex:1;min-height:0;overflow:hidden;position:relative}

.od-tabs{display:flex;flex-direction:column;padding:6px 0;background:#f8fafc;border-right:1px solid #e2e8f0;min-width:110px;flex-shrink:0;overflow-y:auto}
.od-tab{padding:9px 12px;font-size:11px;font-weight:500;color:#64748b;cursor:pointer;border:none;background:none;border-left:3px solid transparent;transition:all .15s;white-space:nowrap;text-align:left;display:flex;align-items:center;justify-content:space-between}
.od-tab:hover{color:#334155;background:rgba(0,0,0,.02)}
.od-tab.active{color:#1d4ed8;border-left-color:#1d4ed8;font-weight:600;background:rgba(29,78,216,.04)}
.od-tab .od-badge{display:inline-flex;align-items:center;justify-content:center;min-width:18px;height:18px;padding:0 5px;border-radius:9px;font-size:9px;font-weight:700;background:#eff6ff;color:#1d4ed8}
.od-tab.active .od-badge{background:#1d4ed8;color:#fff}

.od-grid-area{flex:1;min-width:0;min-height:0;overflow:hidden;position:relative}
.od-grid-container{display:none;position:absolute;top:0;left:0;right:0;bottom:0;overflow:hidden}
.od-grid-container.active{display:flex;flex-direction:column}
.od-dashboard-view{display:none;position:absolute;top:0;left:0;right:0;bottom:0;overflow-y:auto;padding:12px;background:#f0f2f5}
.od-dashboard-view.active{display:block}
#dashEmbed{font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#1a1a2e;display:flex;flex-direction:column;gap:12px;min-height:100%}
#dashEmbed .ds-grid{display:grid !important;grid-template-columns:repeat(6,1fr) !important;gap:10px;width:100% !important}
#dashEmbed .ds-card{background:#fff;border-radius:10px;padding:14px;box-shadow:0 1px 3px rgba(0,0,0,.06);border:1px solid #f1f5f9;position:relative;overflow:hidden;display:flex;flex-direction:column;min-width:0}
#dashEmbed .ds-card-top{display:flex;align-items:center;gap:10px;margin-bottom:6px}
#dashEmbed .ds-card-icon{width:38px;height:38px;border-radius:8px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
#dashEmbed .ds-card-icon svg{width:18px;height:18px}
#dashEmbed .ds-card-icon.teal{background:#f0fdfa;color:#0f766e}
#dashEmbed .ds-card-icon.blue{background:#eff6ff;color:#1d4ed8}
#dashEmbed .ds-card-icon.amber{background:#fffbeb;color:#d97706}
#dashEmbed .ds-card-icon.red{background:#fef2f2;color:#dc2626}
#dashEmbed .ds-card-icon.purple{background:#faf5ff;color:#7c3aed}
#dashEmbed .ds-card-label{font-size:9px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.5px}
#dashEmbed .ds-card-value{font-size:22px;font-weight:800;color:#0f172a;line-height:1}
#dashEmbed .ds-card-footer{display:flex;justify-content:space-between;font-size:9px;color:#64748b;margin-top:auto;padding-top:4px}
#dashEmbed .ds-card-footer span{display:flex;align-items:center;gap:3px}
#dashEmbed .ds-card-spark{position:absolute;bottom:8px;right:8px;width:70px;height:30px;opacity:.5}
#dashEmbed .ds-progress{display:flex;height:5px;border-radius:3px;overflow:hidden;gap:2px;margin-top:6px}
#dashEmbed .ds-progress div{height:100%;border-radius:3px}
#dashEmbed .ds-alert-count{width:44px;height:44px;border-radius:50%;background:#dc2626;color:#fff;display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:800;margin:6px auto}
#dashEmbed .ds-gauge-wrap{display:flex;align-items:center;justify-content:center;margin:4px auto}
#dashEmbed .db-row{display:grid;grid-template-columns:1fr 2fr 1fr;gap:12px;flex:1;min-height:0;overflow:hidden}
#dashEmbed .db-panel{background:#fff;border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,.06);border:1px solid #f1f5f9;display:flex;flex-direction:column;min-height:0;overflow:hidden}
#dashEmbed .db-panel-hdr{padding:12px 16px;border-bottom:1px solid #f1f5f9;flex-shrink:0}
#dashEmbed .db-panel-hdr h3{font-size:13px;font-weight:700;color:#0f172a;margin:0;display:flex;align-items:center;gap:6px}
#dashEmbed .db-panel-hdr h3 .dot{width:7px;height:7px;border-radius:50%;background:#0f766e}
#dashEmbed .db-panel-body{flex:1;padding:12px 16px;overflow-y:auto;min-height:0;display:flex;flex-direction:column}
#dashEmbed .db-tabs{display:flex;gap:0;margin-bottom:10px;border:1px solid #e2e8f0;border-radius:6px;overflow:hidden}
#dashEmbed .db-tab{flex:1;padding:7px 12px;text-align:center;font-size:11px;font-weight:600;cursor:pointer;background:#fff;color:#64748b;border:none;transition:all .15s}
#dashEmbed .db-tab.active{background:#0f766e;color:#fff}
#dashEmbed .db-tab .badge{display:inline-flex;align-items:center;justify-content:center;min-width:18px;height:18px;padding:0 5px;border-radius:9px;font-size:9px;font-weight:700;margin-left:3px}
#dashEmbed .db-tab.active .badge{background:rgba(255,255,255,.25);color:#fff}
#dashEmbed .db-tab .badge.green{background:#dcfce7;color:#16a34a}
#dashEmbed .db-tab .badge.red{background:#fee2e2;color:#dc2626}
#dashEmbed .db-tab .badge.blue{background:#dbeafe;color:#2563eb}
#dashEmbed .db-table{width:100%;border-collapse:collapse;font-size:11px}
#dashEmbed .db-table th{background:#1e293b;color:#fff;padding:9px 10px;text-align:left;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;white-space:nowrap}
#dashEmbed .db-table td{padding:9px 10px;border-bottom:1px solid #f1f5f9;color:#1e293b;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:140px}
#dashEmbed .db-table tr:hover{background:#f8fafc}
#dashEmbed .db-pri{display:inline-flex;align-items:center;gap:3px;padding:2px 8px;border-radius:8px;font-size:9px;font-weight:600}
#dashEmbed .db-pri.high{background:#fef2f2;color:#dc2626}
#dashEmbed .db-pri.low{background:#f0fdf4;color:#16a34a}
#dashEmbed .db-status{display:inline-flex;align-items:center;gap:3px;padding:2px 8px;border-radius:8px;font-size:9px;font-weight:600;background:#eff6ff;color:#1d4ed8}
#dashEmbed .db-timer{font-size:10px;color:#64748b;font-variant-numeric:tabular-nums}
#dashEmbed .chart-wrap{position:relative;width:100%;flex:1;min-height:0}
#dashEmbed .chart-wrap canvas{width:100%!important;height:100%!important}
.od-grid-container .slick-viewport{flex:1;overflow:auto!important;min-height:0}
#todaySamplesCollectedListContainer,#backlogSamplesCollectedListContainer{width:100%!important;background:#fff!important;height:100%!important}
#todaySamplesCollectedListContainer-slick-grid,#backlogSamplesCollectedListContainer-slick-grid{width:100%!important;height:100%!important}

.od-grid-container .slick-header{background:#1e293b!important;border-bottom:2px solid #0f172a!important;width:100%!important}
.od-grid-container .slick-header-column{font-size:10px!important;font-weight:700!important;color:#fff!important;text-transform:uppercase!important;letter-spacing:.3px!important;padding:0 8px!important;height:36px!important;line-height:36px!important;background:#1e293b!important;border-color:#334155!important;white-space:nowrap!important;box-sizing:border-box!important}
.od-grid-container .slick-header-column:hover{background:#334155!important}
.od-grid-container .slick-headerrow{background:#f1f5f9!important;width:100%!important}
.od-grid-container .slick-headerrow-column{background:#f1f5f9!important;border-color:#e2e8f0!important;padding:3px 4px!important;box-sizing:border-box!important}
.od-grid-container .slick-headerrow-column input{box-sizing:border-box!important;border:1px solid #94a3b8!important;border-radius:4px!important;padding:3px 6px!important;font-size:11px!important;color:#1e293b!important;background:#fff!important;width:100%!important;height:24px!important;line-height:24px!important}
.od-grid-container .slick-headerrow-column input:focus{border-color:#0f766e!important;outline:none!important;box-shadow:0 0 0 2px rgba(15,118,110,.12)!important}
.od-grid-container .slick-row{border-bottom:1px solid #e2e8f0!important;min-height:36px!important;transition:background-color 120ms ease-in-out!important;cursor:pointer!important}
.od-grid-container .slick-row:hover{background:#e0f2fe!important}
.od-grid-container .slick-cell{font-size:12px!important;color:#1e293b!important;padding:0 8px!important;height:36px!important;border-color:#e2e8f0!important;line-height:36px!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;box-sizing:border-box!important}
.od-grid-container .slick-cell:hover{background:rgba(224,242,254,.3)!important}
.od-grid-container .slick-row.odd{background:#f8fafc!important}
.od-grid-container .slick-row.even{background:#fff!important}
.od-grid-container .slick-cell{background:transparent!important}
.od-grid-container .slick-row.od-row-selected,.od-grid-container .slick-row.od-row-selected.odd,.od-grid-container .slick-row.od-row-selected.even{background:#fed7aa!important;border-left:3px solid #ea580c!important}
.od-grid-container .slick-row.od-row-selected .slick-cell{background:transparent!important}
.od-grid-container .slick-cell img{max-height:20px;max-width:20px;vertical-align:middle;display:inline-block!important}
.od-grid-container .slick-cell a{text-decoration:none;display:inline;vertical-align:middle;white-space:nowrap}
.od-grid-container .slick-viewport::-webkit-scrollbar{width:6px;height:6px}
.od-grid-container .slick-viewport::-webkit-scrollbar-track{background:#f1f5f9;border-radius:3px}
.od-grid-container .slick-viewport::-webkit-scrollbar-thumb{background:#94a3b8;border-radius:3px}
.od-grid-container .slick-viewport::-webkit-scrollbar-thumb:hover{background:#64748b}

.od-patient-panel{display:none;background:#fff;border-radius:8px 8px 0 0;box-shadow:0 -2px 12px rgba(0,0,0,.12);border:1px solid #e2e8f0;border-left:4px solid #1d4ed8;position:fixed;bottom:0;left:16px;right:16px;z-index:200;height:220px;max-height:35vh;overflow-y:scroll}
.od-patient-panel.show{display:block}
.od-patient-panel::-webkit-scrollbar{width:6px}
.od-patient-panel::-webkit-scrollbar-track{background:#f1f5f9;border-radius:3px}
.od-patient-panel::-webkit-scrollbar-thumb{background:#94a3b8;border-radius:3px}
.od-patient-panel::-webkit-scrollbar-thumb:hover{background:#64748b}
.od-patient-panel-header{display:flex;align-items:center;gap:8px;padding:10px 16px;background:linear-gradient(135deg,#eff6ff,#f8fafc);border-bottom:1px solid #e2e8f0}
.od-patient-panel-header svg{width:18px;height:18px;color:#1d4ed8;flex-shrink:0;stroke-width:2.2}
.od-patient-panel-header span{font-size:13px;font-weight:700;color:#0f172a;letter-spacing:.2px}
.od-patient-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:0;padding:0}
.od-patient-field{padding:10px 16px;border-right:1px solid #f1f5f9;border-bottom:1px solid #f1f5f9}
.od-patient-field:nth-child(4n){border-right:none}
.od-patient-field label{font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:.5px;font-weight:700;margin-bottom:3px;display:block}
.od-patient-field span{font-size:13px;color:#0f172a;font-weight:600;word-break:break-word;line-height:1.3}
.od-patient-panel-header button{color:#64748b}
.od-patient-panel-header button:hover{color:#0f172a}

.od-customize-wrapper{position:relative}
.od-customize-dropdown{display:none;position:absolute;top:calc(100% + 4px);right:0;background:#fff;border:1px solid #e2e8f0;border-radius:8px;box-shadow:0 6px 16px rgba(0,0,0,.1);z-index:100;min-width:200px;padding:6px 0}
.od-customize-dropdown.open{display:block}
.od-customize-header{padding:6px 12px 4px;font-size:10px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.4px;border-bottom:1px solid #f1f5f9;margin-bottom:2px}
.od-customize-item{display:flex;align-items:center;gap:8px;padding:5px 12px;cursor:pointer;transition:background .15s}
.od-customize-item:hover{background:#f8fafc}
.od-customize-item label{display:flex;align-items:center;gap:8px;cursor:pointer;font-size:11px;color:#1e293b;font-weight:500;flex:1}
.od-customize-item input[type="checkbox"]{width:14px;height:14px;accent-color:#1d4ed8;cursor:pointer;flex-shrink:0}
.od-customize-item .od-card-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}

.hide{display:none!important}

@media(max-width:768px){
    .od-header{flex-direction:column;align-items:flex-start;gap:4px}
    .od-stats{grid-template-columns:repeat(3,1fr);gap:4px}
    .od-section-body{flex-direction:column}
    .od-tabs{flex-direction:row;border-right:none;border-bottom:1px solid #e2e8f0;min-width:0}
    .od-tab{border-left:none;border-bottom:3px solid transparent;padding:7px 10px}
    .od-tab.active{border-bottom-color:#1d4ed8}
.od-patient-grid{grid-template-columns:repeat(2,1fr)}
.od-patient-field:nth-child(4n){border-right:1px solid #f1f5f9}
.od-patient-field:nth-child(2n){border-right:none}
}
</style>

<div class="od-body">
    <div class="od-sticky-top">
        <div class="od-header">
            <div class="od-header-left">
                <div class="od-logo">L</div>
                <div>
                    <h1 class="od-title">Samples Collected</h1>
                    <p class="od-subtitle"><%= serverNow %></p>
                </div>
            </div>
            <div class="od-header-right">
                <div class="od-nav-group">
                    <a href="LabDashboard.do" class="od-nav-btn">Lab Dashboard</a>
                    <a href="SamplesToCollect.do" class="od-nav-btn">Samples to Collect</a>
                    <a href="SamplesCollected.do" class="od-nav-btn active">Samples Collected</a>
                </div>
                <% if (selectedLabLocationName != null && !selectedLabLocationName.isEmpty()) { %>
                <div class="od-location-badge">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
                    <%= selectedLabLocationName %>
                </div>
                <% } %>
                <div class="od-customize-wrapper">
                    <button class="od-customize-btn" id="od-customize-toggle">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
                        Customize
                    </button>
                    <div class="od-customize-dropdown" id="od-customize-dropdown">
                        <div class="od-customize-header">Show / Hide Cards</div>
                        <div class="od-customize-item"><input type="checkbox" id="od-toggle-collect" data-card="collect" checked><label for="od-toggle-collect"><span class="od-card-dot" style="background:#14b8a6"></span>Samples to Collect</label></div>
                        <div class="od-customize-item"><input type="checkbox" id="od-toggle-collected" data-card="collected" checked><label for="od-toggle-collected"><span class="od-card-dot" style="background:#3b82f6"></span>Samples Collected</label></div>
                        <div class="od-customize-item"><input type="checkbox" id="od-toggle-testing" data-card="testing" checked><label for="od-toggle-testing"><span class="od-card-dot" style="background:#f59e0b"></span>Awaiting Testing</label></div>
                        <div class="od-customize-item"><input type="checkbox" id="od-toggle-validation" data-card="validation" checked><label for="od-toggle-validation"><span class="od-card-dot" style="background:#7c3aed"></span>Awaiting Validation</label></div>
                        <div class="od-customize-item"><input type="checkbox" id="od-toggle-completed" data-card="completed" checked><label for="od-toggle-completed"><span class="od-card-dot" style="background:#22c55e"></span>Completed</label></div>
                        <div class="od-customize-item"><input type="checkbox" id="od-toggle-patients" data-card="patients" checked><label for="od-toggle-patients"><span class="od-card-dot" style="background:#e11d48"></span>Total Patients Today</label></div>
                    </div>
                </div>
                <button id="refreshButton" class="od-refresh-btn" onclick="location.href='SamplesCollected.do'">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 4v6h-6"/><path d="M1 20v-6h6"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
                    Refresh
                </button>
            </div>
        </div>
        <div class="od-stats" id="todayStat">
            <div class="od-stat-card" data-card="collect"><div class="od-stat-icon teal"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg></div><div class="od-stat-info"><div class="od-stat-label">To Collect</div><div class="od-stat-value" id="samplesToCollect">0</div></div></div>
            <div class="od-stat-card od-card-highlight" data-card="collected"><div class="od-stat-icon blue"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg></div><div class="od-stat-info"><div class="od-stat-label">Collected</div><div class="od-stat-value" id="samplesCollected">0</div></div></div>
            <div class="od-stat-card" data-card="testing"><div class="od-stat-icon amber"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg></div><div class="od-stat-info"><div class="od-stat-label">Testing</div><div class="od-stat-value" id="awaitingTestCount">0</div></div></div>
            <div class="od-stat-card" data-card="validation" style="<% if (!alwaysValidate) { %> display:none <% } %>"><div class="od-stat-icon purple"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg></div><div class="od-stat-info"><div class="od-stat-label">Validation</div><div class="od-stat-value" id="awaitingValidationCount">0</div></div></div>
            <div class="od-stat-card" data-card="completed"><div class="od-stat-icon green"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg></div><div class="od-stat-info"><div class="od-stat-label">Completed</div><div class="od-stat-value" id="completedTestCount">0</div></div></div>
            <div class="od-stat-card" data-card="patients"><div class="od-stat-icon rose"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg></div><div class="od-stat-info"><div class="od-stat-label">Patients</div><div class="od-stat-value" id="totalCollectedTodayCount">0</div></div></div>
        </div>
    </div>

    <div class="od-main-content">
    <span id="translatedColumnNames"
        data-patientID='<bean:message key="dashboard.sample.column.patientID"/>'
        data-patientName='<bean:message key="dashboard.sample.column.patientName"/>'
        data-source='<bean:message key="dashboard.sample.column.source"/>'
        data-sectionNames='<bean:message key="dashboard.sample.column.sectionNames"/>'
        data-sampleType='<bean:message key="dashboard.sample.column.sampleType"/>'
        data-priority='<bean:message key="dashboard.sample.column.priority"/>'
        data-total='<bean:message key="dashboard.sample.column.total"/>'
        data-notes='<bean:message key="dashboard.sample.column.notes"/>'
        data-action='<bean:message key="dashboard.sample.column.action"/>'
        data-accessionNumber='<bean:message key="dashboard.sample.column.accessionNumber"/>'
        data-pendingTests='<bean:message key="dashboard.sample.column.pendingTests"/>'
        data-pendingValidation='<bean:message key="dashboard.sample.column.pendingValidation"/>'
        data-referredTests='<bean:message key="dashboard.sample.column.referredTests"/>'
        data-completed='<bean:message key="dashboard.sample.column.completed"/>'
        data-printed='<bean:message key="dashboard.sample.column.printed"/>'
        data-tat='<bean:message key="dashboard.sample.column.tat"/>'
        data-link-collectSample='<bean:message key="dashboard.sample.column.link.collectSample"/>'
        data-link-result='<bean:message key="dashboard.sample.column.link.result"/>'
        data-link-validate='<bean:message key="dashboard.sample.column.link.validate"/>'
        data-link-print='<bean:message key="dashboard.sample.column.link.print"/>'
        data-link-label='<bean:message key="dashboard.sample.column.link.label"/>'
    ></span>

    <div class="od-section">
        <div class="od-section-body" style="flex-direction:column">
            <div style="display:flex;flex:1;min-height:0;overflow:hidden">
                <div class="od-tabs" id="od-tabs">
                    <button class="od-tab" data-tab="-1">Dashboard</button>
                    <button class="od-tab active" data-tab="0">Today <span class="od-badge" id="od-today-collected-badge">0</span></button>
                    <button class="od-tab" data-tab="1">Backlog <span class="od-badge" id="od-backlog-collected-badge">0</span></button>
                </div>
                <div class="od-grid-area" id="od-grid-area">
                    <div class="od-dashboard-view" id="od-dashboard-view">
                        <div id="dashEmbed"></div>
                    </div>
                    <div class="od-grid-container" id="todaySamplesCollectedListContainer"><div id="todaySamplesCollectedListContainer-slick-grid"></div></div>
                    <div class="od-grid-container" id="backlogSamplesCollectedListContainer"><div id="backlogSamplesCollectedListContainer-slick-grid"></div></div>
                </div>
            </div>
        </div>
    </div>
    <div id="patientDetails" class="od-patient-panel">
        <div class="od-patient-panel-header">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            <span style="flex:1">Patient Details</span>
            <button onclick="jQuery('#patientDetails').removeClass('show')" style="background:none;border:none;cursor:pointer;padding:2px 6px;border-radius:4px;display:flex;align-items:center;transition:background .15s" onmouseover="this.style.background='#e2e8f0'" onmouseout="this.style.background='none'"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><path d="M18 6 6 18M6 6l12 12"/></svg></button>
        </div>
        <div class="od-patient-grid">
            <div class="od-patient-field"><label>Patient ID</label><span id="patientId"></span></div>
            <div class="od-patient-field"><label>Name</label><span id="name"></span></div>
            <div class="od-patient-field"><label>Father/Husband</label><span id="primaryRelative"></span></div>
            <div class="od-patient-field"><label>Village</label><span id="village"></span></div>
            <div class="od-patient-field"><label>Gender</label><span id="gender"></span></div>
            <div class="od-patient-field"><label>Age</label><span id="age"></span></div>
            <div class="od-patient-field" style="grid-column:1/-1;background:#f0fdfa"><label>Tests</label><span id="patientTests" style="font-size:12px;line-height:1.5"></span></div>
        </div>
    </div>
    </div>

    <div id="labelPrintModel" class="hide details">
        <div class="modal-content">
            <div class="col-12" style="display:inline-block;margin-right:10px">
                <div id="labelDetails">
                    <div style="font-family:sans-serif;font-size:8px;margin-right:15px;margin-top:-4px;margin-bottom:2px">
                        <span class='label-value' id="patientName"></span><br/>
                        <span class='label-value' style="font-size:10px;font-weight:bolder" id="labelPatientId"></span>
                        <span class='label-value' style="padding-left:5px;font-size:10px;font-weight:bolder" id="patientGender"></span>
                        <span class='label-value' style="padding-left:5px;font-size:10px;font-weight:bolder" id="patientAge"></span>
                    </div>
                    <svg style="margin-left:-10px;margin-bottom:-20px;height:50px" id="barcode"></svg>
                </div>
            </div>
        </div>
    </div>
</div>

<script type="text/javascript">
var options={enableColumnReorder:false,enableCellNavigation:true,showHeaderRow:true,headerRowHeight:30,explicitInitialization:true,forceFitColumns:true,rowHeight:36,defaultColumnWidth:110};

var showStats=function(s){
    jQuery("#awaitingTestCount").text(s.awaitingTestCount);
    jQuery("#awaitingValidationCount").text(s.awaitingValidationCount);
    jQuery("#completedTestCount").text(s.completedTestCount);
    jQuery("#totalCollectedTodayCount").text(s.totalCollectedTodayCount);
    jQuery("#samplesToCollect").text(s.samplesToCollect);
    jQuery("#samplesCollected").text(s.samplesCollected);
}

jQuery(document).ready(function(){
    var selectedLabLocationName='<%= selectedLabLocationName.replaceAll("'", "\\\\'") %>';

    function matchesLocationFilter(order){
        if(!selectedLabLocationName)return true;
        var c=(order.comments||order.clinicalDataNotes||"")+"";
        var m=c.match(/\[LAB_LOCATION:([^\]]+)\]/);
        if(!m)return true;
        return m[1].trim().toLowerCase()===selectedLabLocationName.trim().toLowerCase();
    }
    function filterByLocation(arr){return selectedLabLocationName?arr.filter(matchesLocationFilter):arr}

    var todayOrderList=JSON.parse('<%=todayOrderListJson%>');
    var todaySampleNotCollectedList=JSON.parse('<%=todaySampleNotCollectedListJson%>');
    var backlogSampleNotCollectedList=JSON.parse('<%=backlogSampleNotCollectedListJson%>');
    var backlogOrderList=JSON.parse('<%=backlogOrderListJson%>');

    todayOrderList=filterByLocation(todayOrderList);
    todaySampleNotCollectedList=filterByLocation(todaySampleNotCollectedList);
    backlogSampleNotCollectedList=filterByLocation(backlogSampleNotCollectedList);
    backlogOrderList=filterByLocation(backlogOrderList);

    // Pre-populate links before grid creation (fixes action column rendering)
    var _alv=<%=alwaysValidate%>;
    todayOrderList.forEach(function(o){o.link=generateAllLinksForOrder(o,_alv)});
    backlogOrderList.forEach(function(o){o.link=generateAllLinksForOrder(o,_alv)});

    var showPriorityColumn=<%=showPriorityColumn%>;

    var isToday=function(d){var n=new Date('<%= serverNow %>');return n.getDate()===d.getDate()&&n.getMonth()===d.getMonth()&&n.getFullYear()===d.getFullYear()};
    var todayStats={
        awaitingTestCount:todayOrderList.filter(function(o){return o.pendingTestCount>0}).length,
        awaitingValidationCount:todayOrderList.filter(function(o){return o.pendingTestCount==0&&o.pendingValidationCount>0}).length,
        completedTestCount:todayOrderList.filter(function(o){return o.isCompleted}).length,
        totalCollectedTodayCount:todayOrderList.filter(function(o){return isToday(new Date(o.enteredDate))}).length,
        samplesToCollect:todaySampleNotCollectedList.length,
        samplesCollected:todayOrderList.length
    };
    showStats(todayStats);

    jQuery("#od-today-collected-badge").text(todayOrderList.length);
    jQuery("#od-backlog-collected-badge").text(backlogOrderList.length);

    if(<%=showReferredTestsCount%>){
        var tObj=new order("#todaySamplesCollectedListContainer-slick-grid",todayOrderList,generateAllLinksForOrder,getColumnsForTodayOrderWithReferredOutTestsCountColumn,<%=alwaysValidate%>,showPriorityColumn);
    }else{
        var tObj=new order("#todaySamplesCollectedListContainer-slick-grid",todayOrderList,generateAllLinksForOrder,getColumnsForTodayOrder,<%=alwaysValidate%>,showPriorityColumn);
    }
    var tDV=new Slick.Data.DataView();
    var tGrid=new Slick.Grid(tObj.div,tDV,tObj.columns,options);
    createGrid(tGrid,tDV,tObj,onRowSelection);

    if(<%=showReferredTestsCount%>){
        var bObj=new order("#backlogSamplesCollectedListContainer-slick-grid",backlogOrderList,generateAllLinksForOrder,getColumnsForBacklogOrderWithReferredOutTestsCountColumn,<%=alwaysValidate%>,showPriorityColumn);
    }else{
        var bObj=new order("#backlogSamplesCollectedListContainer-slick-grid",backlogOrderList,generateAllLinksForOrder,getColumnsForBacklogOrder,<%=alwaysValidate%>,showPriorityColumn);
    }
    var bDV=new Slick.Data.DataView();
    var bGrid=new Slick.Grid(bObj.div,bDV,bObj.columns,options);
    createGrid(bGrid,bDV,bObj,onRowSelection);

    var todayContainerEl=document.getElementById('todaySamplesCollectedListContainer');
    var backlogContainerEl=document.getElementById('backlogSamplesCollectedListContainer');
    var dashboardViewEl=document.getElementById('od-dashboard-view');

    var allGrids=[
        {grid:tGrid,el:todayContainerEl},
        {grid:bGrid,el:backlogContainerEl}
    ];

    allGrids.forEach(function(g){
        if(g.grid&&g.grid.onClick){g.grid.onClick.subscribe(function(e,args){
            var el=jQuery(args.grid.getContainerNode());el.find('.slick-row').removeClass('od-row-selected');
            var rn=args.grid.getCellNode(args.row,0);if(rn)jQuery(rn).closest('.slick-row').addClass('od-row-selected');
        })}
    });

    function showGrid(index){
        dashboardViewEl.className='od-dashboard-view';
        allGrids.forEach(function(g,i){
            if(!g.el)return;
            if(i===index){
                g.el.className='od-grid-container active';
                if(g.grid&&g.grid.resizeCanvas){
                    setTimeout(function(){
                        g.grid.resizeCanvas();
                        if(g.grid.autosizeColumns) g.grid.autosizeColumns();
                        g.grid.invalidate();
                    },50);
                }
            }else{
                g.el.className='od-grid-container';
            }
        });
    }

    jQuery(window).on('resize', function(){
        allGrids.forEach(function(g){
            if(g.grid && g.grid.resizeCanvas){
                g.grid.resizeCanvas();
                if(g.grid.autosizeColumns) g.grid.autosizeColumns();
                g.grid.invalidate();
            }
        });
    });

    function showDashboard(){
        allGrids.forEach(function(g){if(g.el)g.el.className='od-grid-container'});
        dashboardViewEl.className='od-dashboard-view active';
    }

    jQuery('.od-tab').on('click',function(){
        var idx=parseInt(jQuery(this).data('tab'));
        jQuery('.od-tab').removeClass('active');jQuery(this).addClass('active');
        if(idx===-1){showDashboard()}else{showGrid(idx)}
    });

    var activeTab=<%= (String)request.getSession().getAttribute("activeTab") %>||0;
    if(activeTab>1)activeTab=0;
    setTimeout(function(){jQuery('.od-tab[data-tab="'+activeTab+'"]').trigger('click')},50);

    jQuery("#todaySamplesCollectedListContainer-slick-grid,#backlogSamplesCollectedListContainer-slick-grid")
        .on("click",".label",function(event){
            var p=event.currentTarget;
            labelSelected(p.getAttribute('stNumber'),p.getAttribute('accessionNumber'),p.getAttribute('collectionDateStr'),jQuery);
        });

    function renderEmbeddedDashboard(){
        var el=document.getElementById('dashEmbed');
        var todayOrders=filterByLocation(JSON.parse('<%=todayOrderListJson%>'));
        var todayNotCollected=filterByLocation(JSON.parse('<%=todaySampleNotCollectedListJson%>'));
        var backlogNotCollected=filterByLocation(JSON.parse('<%=backlogSampleNotCollectedListJson%>'));

        var sv={
            tc:todayNotCollected.length,sc:todayOrders.length,
            at:todayOrders.filter(function(o){return o.pendingTestCount>0}).length,
            av:todayOrders.filter(function(o){return o.pendingTestCount==0&&o.pendingValidationCount>0}).length,
            co:todayOrders.filter(function(o){return o.isCompleted}).length
        };

        var icons={
            tc:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/></svg>',
            sc:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
            at:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
            pr:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>',
            ca:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
            ta:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z"/><path d="M12 6v6l4 2"/></svg>'
        };
        function spark(d,w,h,c){
            var s='<svg width="'+w+'" height="'+h+'" viewBox="0 0 '+w+' '+h+'">';
            var mx=Math.max.apply(null,d),mn=Math.min.apply(null,d),rn=mx-mn||1;var pts=[];
            for(var i=0;i<d.length;i++){var x=i*(w/(d.length-1)),y=h-((d[i]-mn)/rn)*(h-4)-2;pts.push(x+','+y)}
            s+='<polyline points="'+pts.join(' ')+'" fill="none" stroke="'+c+'" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>';
            s+='<linearGradient id="sg2_'+c.replace('#','')+'" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="'+c+'" stop-opacity=".3"/><stop offset="100%" stop-color="'+c+'" stop-opacity="0"/></linearGradient>';
            s+='<polygon points="0,'+h+' '+pts.join(' ')+' '+w+','+h+'" fill="url(#sg2_'+c.replace('#','')+')"/></svg>';return s;
        }

        var html='<div class="ds-grid">';
        html+='<div class="ds-card"><div class="ds-card-top"><div class="ds-card-icon teal">'+icons.tc+'</div><div><div class="ds-card-label">SAMPLES TO COLLECT</div><div class="ds-card-value">'+sv.tc+'</div></div></div><div class="ds-card-footer"><span>Samples to Collect</span><span>'+sv.tc+' samples</span></div><div class="ds-card-spark">'+spark([3,5,2,7,4,6,3,8,5,4],70,30,'#0f766e')+'</div></div>';
        html+='<div class="ds-card"><div class="ds-card-top"><div class="ds-card-icon blue">'+icons.sc+'</div><div><div class="ds-card-label">SAMPLES COLLECTED</div><div class="ds-card-value">'+sv.sc+'</div></div></div><div class="ds-card-footer"><span>Last 24 hours trend:</span><span>'+sv.sc+'/'+(sv.sc+5)+'</span></div><div class="ds-card-spark">'+spark([2,4,6,3,5,7,4,6,8,5],70,30,'#1d4ed8')+'</div></div>';
        html+='<div class="ds-card"><div class="ds-card-top"><div class="ds-card-icon amber">'+icons.at+'</div><div><div class="ds-card-label">AWAITING TESTING</div><div class="ds-card-value">'+sv.at+'</div></div></div><div class="ds-card-footer"><span>Last 24 hours trend:</span><span>'+sv.at+' Awaiting testing</span></div><div class="ds-card-spark">'+spark([4,3,5,2,6,4,3,5,7,4],70,30,'#d97706')+'</div></div>';
        html+='<div class="ds-card"><div class="ds-card-top"><div class="ds-card-icon" style="background:#faf5ff;color:#7c3aed">'+icons.pr+'</div><div><div class="ds-card-label">PENDING RESULTS</div><div class="ds-card-value">0</div></div></div><div class="ds-progress"><div style="width:30%;background:#16a34a"></div><div style="width:25%;background:#eab308"></div><div style="width:20%;background:#f97316"></div><div style="width:25%;background:#dc2626"></div></div><div class="ds-card-footer"><span>STAT: 0</span><span>Routine: 0</span><span>Result: 0</span></div></div>';
        html+='<div class="ds-card"><div class="ds-card-top"><div class="ds-card-icon red">'+icons.ca+'</div><div><div class="ds-card-label">CRITICAL ALERTS</div><div class="ds-card-value">0</div></div></div><div class="ds-alert-count">0</div></div>';
        html+='<div class="ds-card"><div class="ds-card-top"><div class="ds-card-icon purple">'+icons.ta+'</div><div><div class="ds-card-label">TAT PERFORMANCE</div><div class="ds-card-value">8.7 ms</div></div></div><div class="ds-gauge-wrap"><svg width="60" height="35" viewBox="0 0 60 35"><path d="M5 30 A25 25 0 0 1 55 30" fill="none" stroke="#e2e8f0" stroke-width="5" stroke-linecap="round"/><path d="M5 30 A25 25 0 0 1 55 30" fill="none" stroke="#7c3aed" stroke-width="5" stroke-linecap="round" stroke-dasharray="78.5" stroke-dashoffset="20"/></svg></div><div class="ds-card-footer"><span>Average:</span><span>8.7 ms</span></div></div>';
        html+='</div>';

        html+='<div class="db-row">';
        html+='<div class="db-panel"><div class="db-panel-hdr"><h3>Workflow Efficiency</h3></div><div class="db-panel-body"><div style="font-size:11px;font-weight:600;color:#0f172a;margin-bottom:6px">Test Turnaround Time by Priority</div><div class="chart-wrap"><canvas id="ewChart2"></canvas></div></div></div>';
        html+='<div class="db-panel"><div class="db-panel-hdr"><h3><span class="dot"></span> Samples to Collect</h3></div><div class="db-panel-body"><div class="db-tabs" id="ecTabs2"></div><div style="overflow-x:auto;flex:1"><table class="db-table"><thead id="ecHead2"></thead><tbody id="ecBody2"></tbody></table></div></div></div>';
        html+='<div class="db-panel"><div class="db-panel-hdr"><h3>Lab Insights</h3></div><div class="db-panel-body"><div style="font-size:11px;font-weight:600;color:#0f172a;margin-bottom:6px">Test Volume by Type</div><div class="chart-wrap"><canvas id="eiChart2"></canvas></div></div></div>';
        html+='</div>';
        el.innerHTML=html;

        var tabs=[{l:'Today',c:todayNotCollected.length,cls:'green'},{l:'Backlog',c:backlogNotCollected.length,cls:'red'},{l:'Backlog',c:todayNotCollected.length+backlogNotCollected.length,cls:'blue'}];
        var th='';tabs.forEach(function(t,i){th+='<button class="db-tab'+(i===0?' active':'')+'" data-didx="'+i+'">'+t.l+' <span class="badge '+t.cls+'">'+t.c+'</span></button>';});
        document.getElementById('ecTabs2').innerHTML=th;
        document.getElementById('ecHead2').innerHTML='<tr><th>Patient ID</th><th>Patient Name</th><th>Priority</th><th>Status</th><th>Sample Collection</th></tr>';
        function rTable(di){
            var d=di===0?todayNotCollected:di===1?backlogNotCollected:todayNotCollected.concat(backlogNotCollected);
            var b='';d.slice(0,8).forEach(function(r){
                var p=(r.priority||'Low').toLowerCase(),pc=p==='high'?'high':'low';
                var sc=Math.floor(Math.random()*60),mn=Math.floor(Math.random()*60);
                b+='<tr><td>'+((r.stNumber||'').substring(0,12))+'</td><td>'+((r.firstName||'')+' '+(r.lastName||'')).substring(0,20)+'</td>';
                b+='<td><span class="db-pri '+pc+'">'+(r.priority||'Low')+'</span> <span class="db-status">Dynamic</span></td>';
                b+='<td>'+Math.floor(Math.random()*12)+'</td><td class="db-timer">00:'+String(mn).padStart(2,'0')+':'+String(sc).padStart(2,'0')+' mm</td></tr>';
            });
            document.getElementById('ecBody2').innerHTML=b;
        }
        rTable(0);
        document.querySelectorAll('[data-didx]').forEach(function(btn){btn.addEventListener('click',function(){
            document.querySelectorAll('[data-didx]').forEach(function(x){x.classList.remove('active')});this.classList.add('active');
            rTable(parseInt(this.dataset.didx));
        });});

        setTimeout(function(){
            var c1=document.getElementById('ewChart2');if(c1){var x1=c1.getContext('2d'),dp=window.devicePixelRatio||1,r1=c1.parentElement.getBoundingClientRect();c1.width=r1.width*dp;c1.height=r1.height*dp;x1.scale(dp,dp);var w=r1.width,h=r1.height;
            x1.fillStyle='#f8fafc';x1.fillRect(0,0,w,h);
            var cats=['STAT','Routine','STAT','Routine'],sd=[42,0,38,0],rd=[0,35,0,45],bw=w/10,mx=50,ch=h-28;
            for(var i=0;i<4;i++){var bx=24+i*((w-48)/4)+bw*0.2;
            x1.fillStyle='#0f766e';x1.beginPath();x1.roundRect(bx,h-22-ch*0.7,bw*0.85,sd[i]/mx*ch||ch*0.7,3);x1.fill();
            if(rd[i]>0){x1.fillStyle='#d97706';x1.beginPath();x1.roundRect(bx+bw*0.3,h-22-rd[i]/mx*ch,bw*0.85,rd[i]/mx*ch,3);x1.fill();}
            x1.fillStyle='#64748b';x1.font='9px sans-serif';x1.textAlign='center';x1.fillText(cats[i],bx+bw*0.5,h-6);}
            x1.fillStyle='#64748b';x1.font='9px sans-serif';x1.textAlign='right';
            for(var v=0;v<=50;v+=10){var y=h-22-(v/mx*ch);x1.fillText(v,18,y+3);x1.strokeStyle='#e2e8f0';x1.lineWidth=.5;x1.beginPath();x1.moveTo(22,y);x1.lineTo(w,y);x1.stroke();}
            x1.fillStyle='#0f766e';x1.fillRect(w-80,h-10,7,7);x1.fillStyle='#64748b';x1.font='9px sans-serif';x1.textAlign='left';x1.fillText('STAT',w-70,h-3);
            x1.fillStyle='#d97706';x1.fillRect(w-38,h-10,7,7);x1.fillStyle='#64748b';x1.fillText('Routine',w-28,h-3);}

            var c2=document.getElementById('eiChart2');if(c2){var x2=c2.getContext('2d'),dp2=window.devicePixelRatio||1,r2=c2.parentElement.getBoundingClientRect();c2.width=r2.width*dp2;c2.height=r2.height*dp2;x2.scale(dp2,dp2);var w2=r2.width,h2=r2.height;
            var labs=['Sun','Mon','Tue','Wed','Thu','Fri','Sat','Dec'],ds=[{d:[80,120,95,180,140,160,110,200],c:'#0f766e'},{d:[60,90,110,150,120,130,95,170],c:'#1d4ed8'},{d:[40,70,80,120,100,110,85,140],c:'#d97706'}],mv=350,ch2=h2-25,pL=28;
            x2.fillStyle='#f8fafc';x2.fillRect(0,0,w2,h2);
            x2.fillStyle='#64748b';x2.font='9px sans-serif';x2.textAlign='right';
            for(var v=0;v<=350;v+=50){var y=h2-25-(v/mv*ch2);x2.fillText(v,pL-4,y+3);x2.strokeStyle='#e2e8f0';x2.lineWidth=.5;x2.beginPath();x2.moveTo(pL,y);x2.lineTo(w2-8,y);x2.stroke();}
            x2.textAlign='center';var st=(w2-pL-8)/(labs.length-1);labs.forEach(function(l,i){x2.fillText(l,pL+i*st,h2-5);});
            ds.forEach(function(s){x2.strokeStyle=s.c;x2.lineWidth=2;x2.beginPath();s.d.forEach(function(v,i){var x=pL+i*st,y=h2-25-(v/mv*ch2);if(i===0)x2.moveTo(x,y);else x2.lineTo(x,y);});x2.stroke();});}
        },200);
    }
    renderEmbeddedDashboard();
});

var printDiv=function(d){var w=window.open('','Print-Window');w.document.open();w.document.write('<html><head><style>@media print{@page{size:100mm 20mm;margin:0mm;font-size:7px}}</style></head><body onload="window.print()">'+document.getElementById(d).innerHTML+'</body></html>');w.document.close();setTimeout(function(){w.close()},10)}

var showLabelDetails=function(n,t,g,b,s,c){jQuery("#patientName").text(n);if(n==='M')g='Male';if(n==='F')g='Female';if(n=='O')g='Other';jQuery("#patientGender").text(g);jQuery("#patientAge").text(b);jQuery('#labelPatientId').text(s);jQuery('#collectionDate').text(c);jQuery('#tests').text(t)}
var showLabelDetailsWithoutPatientDetails=function(s,c){jQuery('#labelPatientId').text(s);jQuery('#secondLabelPatientId').text(s);jQuery('#collectionDate').text(c);jQuery('#secondLabelCollectionDate').text(c)}

function labelSelected(st,an,cd,j){
    new Ajax.Request('ajaxQueryXML',{method:'get',parameters:"provider=OrderedTestsPopulateProvider&accessionNumber="+an,
        onSuccess:function(xhr){
            var dp='<%=SystemConfiguration.getInstance().getPatternForDateLocale()%>',sp='<%=showPatientsDetailsInSampleLabelPrint%>';
            if(sp==='true')showLabelDetails(OpenElis.Utils.getXMLValue(xhr.responseXML,'patientName'),OpenElis.Utils.getXMLValue(xhr.responseXML,'tests'),OpenElis.Utils.getXMLValue(xhr.responseXML,'gender'),OpenElis.Utils.calculateAge(OpenElis.Utils.getXMLValue(xhr.responseXML,'birth_date'),dp),st,cd);
            else showLabelDetailsWithoutPatientDetails(st,cd);
            j(".accessionNumber").html(an);j("#barcode").JsBarcode(an,{width:1.1,height:25,fontSize:9});printDiv('labelPrintModel');
        }
    });
}

var showPatientDetails=function(s,f,m,l,p,v,g,a){var el=document.getElementById('patientDetails');el.classList.add('show');document.getElementById('patientId').textContent=s||'N/A';document.getElementById('name').textContent=f+" "+(m?m+" ":"")+l;document.getElementById('primaryRelative').textContent=p||'N/A';document.getElementById('village').textContent=v||'N/A';document.getElementById('gender').textContent=g;document.getElementById('age').textContent=a}

function onRowSelection(r){
    if(r.stNumber)new Ajax.Request('ajaxQueryXML',{method:'get',parameters:"provider=PatientSearchPopulateProvider&stNumber="+r.stNumber,onSuccess:onRowSelectionSuccess});
    if(r.accessionNumber){
        new Ajax.Request('ajaxQueryXML',{method:'get',parameters:"provider=OrderedTestsPopulateProvider&accessionNumber="+r.accessionNumber,onSuccess:function(xhr){jQuery("#patientTests").text(OpenElis.Utils.getXMLValue(xhr.responseXML,'tests')||"N/A")}});
    }else{
        jQuery("#patientTests").text(r.testNames||(r.totalTestCount?r.totalTestCount+" test(s)":"N/A"));
    }
}
function onRowSelectionSuccess(xhr){
    var dp='<%=SystemConfiguration.getInstance().getPatternForDateLocale()%>';
    showPatientDetails(OpenElis.Utils.getXMLValue(xhr.responseXML,'ST_ID'),OpenElis.Utils.getXMLValue(xhr.responseXML,'firstName'),OpenElis.Utils.getXMLValue(xhr.responseXML,'middleName'),OpenElis.Utils.getXMLValue(xhr.responseXML,'lastName'),OpenElis.Utils.getXMLValue(xhr.responseXML,'primaryRelative'),getAddressValue(xhr.responseXML,1),OpenElis.Utils.getXMLValue(xhr.responseXML,'gender'),OpenElis.Utils.calculateAge(OpenElis.Utils.getXMLValue(xhr.responseXML,'dob'),dp));
}
function getAddressValue(r,i){var f=r.getElementsByTagName('addressline').item(i),v=f&&f.getElementsByTagName('value').item(0);return v!=null&&v.firstChild!=null?v.firstChild.nodeValue:""}

(function(){
    var K='od_dashboard_visibility',t=document.getElementById('od-customize-toggle'),d=document.getElementById('od-customize-dropdown');
    if(!t||!d)return;
    function gp(){try{var r=localStorage.getItem(K);return r?JSON.parse(r):null}catch(e){return null}}
    function sp(p){try{localStorage.setItem(K,JSON.stringify(p))}catch(e){}}
    function ap(){var p=gp()||{},cbs=d.querySelectorAll('input[type="checkbox"]');cbs.forEach(function(cb){var k=cb.getAttribute('data-card'),card=document.querySelector('.od-stat-card[data-card="'+k+'"]');if(!card)return;var v=p.hasOwnProperty(k)?p[k]:true;cb.checked=v;if(v)card.classList.remove('od-card-hidden');else card.classList.add('od-card-hidden')})}
    t.addEventListener('click',function(e){e.stopPropagation();d.classList.toggle('open')});
    document.addEventListener('click',function(e){if(!d.contains(e.target)&&e.target!==t)d.classList.remove('open')});
    d.addEventListener('click',function(e){e.stopPropagation()});
    var cbs=d.querySelectorAll('input[type="checkbox"]');cbs.forEach(function(cb){cb.addEventListener('change',function(){var k=this.getAttribute('data-card'),card=document.querySelector('.od-stat-card[data-card="'+k+'"]');if(!card)return;if(this.checked)card.classList.remove('od-card-hidden');else card.classList.add('od-card-hidden');var p={};cbs.forEach(function(c){p[c.getAttribute('data-card')]=c.checked});sp(p)})});
    ap();
})();
</script>
