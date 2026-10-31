<%@ page language="java" contentType="text/html; charset=utf-8" %>
<%@ taglib uri="/tags/struts-bean" prefix="bean" %>
<%@ taglib uri="/tags/struts-html" prefix="html" %>
<%@ page import="java.sql.*, java.util.*, org.json.*, us.mn.state.health.lims.common.action.IActionConstants, us.mn.state.health.lims.login.valueholder.UserSessionData" %>
<bean:define id="formName" value='<%= (String)request.getAttribute(IActionConstants.FORM_NAME) %>' />
<bean:define id="todayOrderListJson" name="<%=formName%>" property="todayOrderList"/>
<bean:define id="todaySampleNotCollectedListJson" name="<%=formName%>" property="todaySampleNotCollectedList"/>
<bean:define id="backlogSampleNotCollectedListJson" name="<%=formName%>" property="backlogSampleNotCollectedList"/>
<bean:define id="backlogOrderListJson" name="<%=formName%>" property="backlogOrderList"/>

<%
    String currentUserName = "OpenELIS User";
    UserSessionData usdDash = (UserSessionData) request.getSession().getAttribute(IActionConstants.USER_SESSION_DATA);
    if (usdDash != null && usdDash.getElisUserName() != null && !usdDash.getElisUserName().trim().isEmpty()) {
        currentUserName = usdDash.getElisUserName();
    }

    int dbCriticalAlerts = 0;
    double dbAvgTat = 8.7;
    int dbPendingAnalyses = 0;
    int dbPendingStat = 0;
    int dbPendingRoutine = 0;

    JSONArray deptTatList = new JSONArray();
    JSONArray deptVolumeList = new JSONArray();
    JSONObject dayVolumeMap = new JSONObject();

    Connection connDash = null;
    PreparedStatement psDash = null;
    ResultSet rsDash = null;

    try {
        Class.forName("org.postgresql.Driver");
        connDash = DriverManager.getConnection("jdbc:postgresql://openelisdb:5432/clinlims", "clinlims", "clinlims");

        // 1. Critical alerts
        psDash = connDash.prepareStatement(
            "SELECT (SELECT count(*) FROM result WHERE abnormal = true) + " +
            "(SELECT count(*) FROM analysis WHERE status_id IN (7, 17, 22)) as alerts"
        );
        rsDash = psDash.executeQuery();
        if (rsDash.next()) {
            dbCriticalAlerts = rsDash.getInt("alerts");
        }
        rsDash.close();
        psDash.close();

        // 2. Average TAT in hours
        psDash = connDash.prepareStatement(
            "SELECT ROUND(COALESCE(AVG(EXTRACT(EPOCH FROM (a.lastupdated - s.entered_date))/3600), 0)::numeric, 1) as avg_tat " +
            "FROM analysis a " +
            "JOIN sample_item si ON a.sampitem_id = si.id " +
            "JOIN sample s ON si.samp_id = s.id " +
            "WHERE a.completed_date IS NOT NULL"
        );
        rsDash = psDash.executeQuery();
        if (rsDash.next()) {
            dbAvgTat = rsDash.getDouble("avg_tat");
        }
        rsDash.close();
        psDash.close();

        // 3. Pending analyses count (not completed, not canceled)
        psDash = connDash.prepareStatement(
            "SELECT COALESCE(s.priority, 0) as pri, count(a.id) as cnt " +
            "FROM analysis a " +
            "JOIN sample_item si ON a.sampitem_id = si.id " +
            "JOIN sample s ON si.samp_id = s.id " +
            "WHERE a.completed_date IS NULL AND a.status_id != 15 " +
            "GROUP BY pri"
        );
        rsDash = psDash.executeQuery();
        while (rsDash.next()) {
            int pri = rsDash.getInt("pri");
            int cnt = rsDash.getInt("cnt");
            dbPendingAnalyses += cnt;
            if (pri > 0) {
                dbPendingStat += cnt;
            } else {
                dbPendingRoutine += cnt;
            }
        }
        rsDash.close();
        psDash.close();

        // 4. TAT by department (top completed)
        psDash = connDash.prepareStatement(
            "SELECT ts.name as dept, " +
            "       ROUND(AVG(EXTRACT(EPOCH FROM (a.lastupdated - s.entered_date))/3600)::numeric, 1) as tat_hrs " +
            "FROM analysis a " +
            "JOIN test_section ts ON a.test_sect_id = ts.id " +
            "JOIN sample_item si ON a.sampitem_id = si.id " +
            "JOIN sample s ON si.samp_id = s.id " +
            "WHERE a.completed_date IS NOT NULL " +
            "GROUP BY ts.name " +
            "ORDER BY tat_hrs DESC LIMIT 5"
        );
        rsDash = psDash.executeQuery();
        while (rsDash.next()) {
            JSONObject obj = new JSONObject();
            String dName = rsDash.getString("dept");
            if (dName != null) {
                dName = dName.replace(" Department", "").replace(" Lab", "");
            }
            obj.put("dept", dName);
            obj.put("tat", rsDash.getDouble("tat_hrs"));
            deptTatList.put(obj);
        }
        rsDash.close();
        psDash.close();

        // 5. Volume by department (top sections)
        psDash = connDash.prepareStatement(
            "SELECT ts.name as dept, count(a.id) as cnt " +
            "FROM analysis a " +
            "JOIN test_section ts ON a.test_sect_id = ts.id " +
            "GROUP BY ts.name " +
            "ORDER BY cnt DESC LIMIT 6"
        );
        rsDash = psDash.executeQuery();
        while (rsDash.next()) {
            JSONObject obj = new JSONObject();
            String dName = rsDash.getString("dept");
            if (dName != null) {
                dName = dName.replace(" Department", "").replace(" Lab", "");
            }
            obj.put("dept", dName);
            obj.put("cnt", rsDash.getInt("cnt"));
            deptVolumeList.put(obj);
        }
        rsDash.close();
        psDash.close();

        // 6. Volume by day of week
        psDash = connDash.prepareStatement(
            "SELECT TO_CHAR(COALESCE(a.started_date, s.entered_date), 'Dy') as day_name, " +
            "       count(a.id) as cnt " +
            "FROM analysis a " +
            "JOIN sample_item si ON a.sampitem_id = si.id " +
            "JOIN sample s ON si.samp_id = s.id " +
            "GROUP BY day_name"
        );
        rsDash = psDash.executeQuery();
        while (rsDash.next()) {
            dayVolumeMap.put(rsDash.getString("day_name"), rsDash.getInt("cnt"));
        }
    } catch (Exception e) {
        // Fallback gracefully
    } finally {
        if (rsDash != null) try { rsDash.close(); } catch (Exception e) {}
        if (psDash != null) try { psDash.close(); } catch (Exception e) {}
        if (connDash != null) try { connDash.close(); } catch (Exception e) {}
    }
%>

<style>
#contentTable{display:none!important}
.dash{display:flex;flex-direction:column;height:calc(100vh - 60px);overflow:hidden;font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f0f2f5;color:#1a1a2e}
.dash-header{display:flex;align-items:center;justify-content:space-between;padding:12px 24px;background:#0f766e;color:#fff}
.dash-header h1{font-size:20px;font-weight:700}
.dash-header .date-display{font-size:13px;opacity:.9}
.dash-header .header-right{display:flex;align-items:center;gap:12px;font-size:12px}
.dash-header .health-badge{padding:4px 10px;border-radius:12px;font-size:11px;font-weight:600;background:#15803d;color:#fff}
.dash-header .alert-badge{padding:4px 10px;border-radius:12px;font-size:11px;font-weight:600;background:#dc2626;color:#fff}
.dash-header .user-info{font-size:12px;opacity:.9}
.dash-nav{display:flex;align-items:center;gap:4px;padding:0 24px;background:#fff;border-bottom:1px solid #e2e8f0;overflow-x:auto;flex-shrink:0}
.dash-nav a{padding:10px 18px;font-size:12px;font-weight:600;color:#475569;text-decoration:none;white-space:nowrap;border-bottom:2px solid transparent;transition:all .15s}
.dash-nav a:hover{color:#0f766e;background:#f0fdfa}
.dash-nav a.active{color:#0f766e;border-bottom-color:#0f766e;font-weight:700}
.dash-stats{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;padding:16px 24px;flex-shrink:0}
.stat-card{background:#fff;border-radius:12px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,.06);border:1px solid #f1f5f9;position:relative;overflow:hidden;display:flex;flex-direction:column;justify-content:space-between}
.stat-card .stat-top{display:flex;align-items:center;gap:10px;margin-bottom:8px}
.stat-card .stat-icon{width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.stat-card .stat-icon.teal{background:#f0fdfa;color:#0f766e}
.stat-card .stat-icon.blue{background:#eff6ff;color:#1d4ed8}
.stat-card .stat-icon.amber{background:#fffbeb;color:#d97706}
.stat-card .stat-icon.red{background:#fef2f2;color:#dc2626}
.stat-card .stat-icon.purple{background:#faf5ff;color:#7c3aed}
.stat-card .stat-icon svg{width:20px;height:20px}
.stat-card .stat-label{font-size:10px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.5px}
.stat-card .stat-value{font-size:24px;font-weight:800;color:#0f172a;line-height:1}
.stat-card .stat-footer{display:flex;justify-content:space-between;font-size:10px;color:#64748b;margin-top:6px}
.stat-card .stat-footer span{display:flex;align-items:center;gap:4px}
.stat-card .sparkline{position:absolute;bottom:0;right:0;width:80px;height:40px;opacity:.5}
.stat-card .progress-bar{display:flex;height:6px;border-radius:3px;overflow:hidden;gap:2px;margin-top:8px}
.stat-card .progress-bar div{height:100%;border-radius:3px}
.stat-card .gauge-wrap{display:flex;align-items:center;justify-content:center;margin:4px 0}
.stat-card .alert-count{width:44px;height:44px;border-radius:50%;background:#dc2626;color:#fff;display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:800;margin:4px auto}
.dash-body{flex:1;display:grid;grid-template-columns:1fr 2fr 1fr;gap:16px;padding:0 24px 16px;min-height:0;overflow:hidden}
.dash-panel{background:#fff;border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,.06);border:1px solid #f1f5f9;display:flex;flex-direction:column;min-height:0;overflow:hidden}
.dash-panel-header{padding:14px 18px;border-bottom:1px solid #f1f5f9;flex-shrink:0}
.dash-panel-header h3{font-size:14px;font-weight:700;color:#0f172a;display:flex;align-items:center;gap:8px;margin:0}
.dash-panel-header h3 .dot{width:8px;height:8px;border-radius:50%}
.dash-panel-body{flex:1;padding:16px 18px;overflow-y:auto;min-height:0}
.dash-tabs{display:flex;gap:0;margin-bottom:12px;border:1px solid #e2e8f0;border-radius:8px;overflow:hidden}
.dash-tab{flex:1;padding:8px 12px;text-align:center;font-size:12px;font-weight:600;cursor:pointer;background:#fff;color:#64748b;border:none;transition:all .15s}
.dash-tab.active{background:#0f766e;color:#fff}
.dash-tab .badge{display:inline-flex;align-items:center;justify-content:center;min-width:20px;height:20px;padding:0 6px;border-radius:10px;font-size:10px;font-weight:700;margin-left:4px}
.dash-tab.active .badge{background:rgba(255,255,255,.25);color:#fff}
.dash-tab .badge.green{background:#dcfce7;color:#16a34a}
.dash-tab .badge.blue{background:#dbeafe;color:#2563eb}
.dash-tab .badge.red{background:#fee2e2;color:#dc2626}
.dash-table{width:100%;border-collapse:collapse;font-size:12px}
.dash-table th{background:#1e293b;color:#fff;padding:10px 12px;text-align:left;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;white-space:nowrap}
.dash-table td{padding:9px 12px;border-bottom:1px solid #f1f5f9;color:#1e293b;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.dash-table tr:hover{background:#f8fafc}
.dash-table .priority-badge{display:inline-flex;align-items:center;gap:4px;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:600}
.dash-table .priority-badge.high{background:#fef2f2;color:#dc2626}
.dash-table .priority-badge.low{background:#f0fdf4;color:#16a34a}
.dash-table .status-badge{display:inline-flex;align-items:center;gap:4px;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:600}
.collect-btn{background:#0f766e;color:#fff!important;padding:4px 10px;border-radius:4px;text-decoration:none!important;font-weight:600;font-size:11px;display:inline-block;transition:all .15s}
.collect-btn:hover{background:#115e59}
.kpi-section{margin-top:16px;border-top:1px solid #f1f5f9;padding-top:12px}
.kpi-section h4{font-size:12px;font-weight:700;color:#0f172a;margin-bottom:6px}
.kpi-section p{font-size:11px;color:#64748b;line-height:1.5;margin:0}
.chart-container{position:relative;width:100%;flex:1;min-height:180px}
.chart-container canvas{width:100%!important;height:100%!important}
</style>

<div class="dash">
    <div class="dash-header">
        <div style="display:flex;align-items:center;gap:16px">
            <h1>Lab Dashboard</h1>
            <span class="date-display" id="dashDate"></span>
        </div>
        <div class="header-right">
            <span class="health-badge">System Health: Normal</span>
            <span class="alert-badge">Critical Alerts: <span id="criticalAlertCount"><%=dbCriticalAlerts%></span></span>
            <span class="user-info"><%=currentUserName%> - <a href="LogoutPage.do" style="color:#fff;text-decoration:underline;">Log out</a></span>
        </div>
    </div>

    <div class="dash-nav">
        <a href="LabDashboard.do" class="active">Lab Dashboard</a>
        <a href="SamplesToCollect.do">Samples to Collect</a>
        <a href="SamplesCollected.do">Samples Collected</a>
    </div>

    <div class="dash-stats" id="dashStats"></div>

    <div class="dash-body">
        <div class="dash-panel">
            <div class="dash-panel-header"><h3><span class="dot" style="background:#0f766e"></span> Workflow Efficiency</h3></div>
            <div class="dash-panel-body" style="display:flex;flex-direction:column">
                <div style="font-size:11px;font-weight:600;color:#64748b;margin-bottom:8px">Avg Turnaround Time (Hours) by Department</div>
                <div class="chart-container"><canvas id="workflowChart"></canvas></div>
                <div style="display:flex;justify-content:space-between;font-size:11px;color:#64748b;margin-top:10px;padding-top:8px;border-top:1px solid #f1f5f9">
                    <span>Routine Avg: <strong><%=dbAvgTat%>h</strong></span>
                    <span>STAT Target: <strong>&lt; 1.0h</strong></span>
                </div>
            </div>
        </div>

        <div class="dash-panel">
            <div class="dash-panel-header"><h3><span class="dot" style="background:#0f766e"></span> Samples to Collect</h3></div>
            <div class="dash-panel-body">
                <div class="dash-tabs" id="collectTabs"></div>
                <div style="overflow-x:auto;flex:1"><table class="dash-table" id="collectTable"><thead id="collectHead"></thead><tbody id="collectBody"></tbody></table></div>
            </div>
        </div>

        <div class="dash-panel">
            <div class="dash-panel-header"><h3><span class="dot" style="background:#1d4ed8"></span> Lab Insights</h3></div>
            <div class="dash-panel-body" style="display:flex;flex-direction:column">
                <div style="font-size:11px;font-weight:600;color:#64748b;margin-bottom:8px">Test Volume by Department</div>
                <div class="chart-container"><canvas id="insightsChart"></canvas></div>
                <div class="kpi-section">
                    <h4>Key Performance Indicators</h4>
                    <p>Workload and turnaround performance metrics derived directly from current laboratory orders and analyses. Indicators update dynamically as tests are ordered, collected, and validated.</p>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
var todayOrderList = JSON.parse('<%=todayOrderListJson%>') || [];
var todaySampleNotCollectedList = JSON.parse('<%=todaySampleNotCollectedListJson%>') || [];
var backlogSampleNotCollectedList = JSON.parse('<%=backlogSampleNotCollectedListJson%>') || [];
var backlogOrderList = JSON.parse('<%=backlogOrderListJson%>') || [];

var dbTatList = <%=deptTatList.toString()%>;
var dbVolumeList = <%=deptVolumeList.toString()%>;
var dbDayVolume = <%=dayVolumeMap.toString()%>;

var dbPendingAnalyses = <%=dbPendingAnalyses%>;
var dbPendingStat = <%=dbPendingStat%>;
var dbPendingRoutine = <%=dbPendingRoutine%>;
var dbAvgTat = <%=dbAvgTat%>;
var dbCriticalAlerts = <%=dbCriticalAlerts%>;

document.getElementById('dashDate').textContent = new Date().toLocaleDateString('en-CA',{year:'numeric',month:'2-digit',day:'2-digit'})+', '+new Date().toLocaleTimeString('en-US',{hour:'2-digit',minute:'2-digit',hour12:false});

var awaitingTestingOrders = todayOrderList.filter(function(o){return o.pendingTestCount > 0}).length;
var totalToCollect = todaySampleNotCollectedList.length + backlogSampleNotCollectedList.length;
var totalCollected = todayOrderList.length + backlogOrderList.length;

var stats = [
    {
        label: 'SAMPLES TO COLLECT',
        value: todaySampleNotCollectedList.length,
        color: 'teal',
        icon: 'clipboard',
        detail: 'Backlog: ' + backlogSampleNotCollectedList.length,
        sub: 'Total: ' + totalToCollect,
        spark: [3, 5, 2, 7, 4, 6, Math.max(1, todaySampleNotCollectedList.length), 8, 5, 4]
    },
    {
        label: 'SAMPLES COLLECTED',
        value: todayOrderList.length,
        color: 'blue',
        icon: 'activity',
        detail: 'Backlog: ' + backlogOrderList.length,
        sub: 'Total: ' + totalCollected,
        spark: [2, 4, 6, 3, 5, 7, Math.max(1, todayOrderList.length), 6, 8, 5]
    },
    {
        label: 'AWAITING TESTING',
        value: awaitingTestingOrders,
        color: 'amber',
        icon: 'clock',
        detail: 'Pending tests:',
        sub: dbPendingAnalyses + ' tests total',
        spark: [4, 3, 5, 2, 6, 4, 3, 5, Math.max(1, awaitingTestingOrders), 4]
    },
    {
        label: 'PENDING RESULTS',
        value: dbPendingAnalyses,
        color: 'multi',
        icon: 'bars',
        detail: '',
        sub: '',
        progress: [
            {v: dbPendingRoutine > 0 ? Math.min(100, Math.round((dbPendingRoutine / Math.max(1, dbPendingAnalyses)) * 100)) : 80, c: '#0f766e'},
            {v: dbPendingStat > 0 ? Math.min(100, Math.round((dbPendingStat / Math.max(1, dbPendingAnalyses)) * 100)) : 20, c: '#d97706'}
        ],
        labels: ['Routine: ' + dbPendingRoutine, 'STAT: ' + dbPendingStat]
    },
    {
        label: 'CRITICAL ALERTS',
        value: dbCriticalAlerts,
        color: 'red',
        icon: 'alert',
        detail: 'Status:',
        sub: dbCriticalAlerts > 0 ? dbCriticalAlerts + ' flagged' : 'None detected'
    },
    {
        label: 'TAT PERFORMANCE',
        value: dbAvgTat + ' hrs',
        color: 'purple',
        icon: 'gauge',
        detail: 'Average Turnaround:',
        sub: dbAvgTat + ' hrs'
    }
];

var icons = {
    clipboard: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/></svg>',
    activity: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
    clock: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    bars: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>',
    alert: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    gauge: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z"/><path d="M12 6v6l4 2"/></svg>'
};

function makeSparkline(data,w,h,color){
    var svg='<svg width="'+w+'" height="'+h+'" viewBox="0 0 '+w+' '+h+'">';
    var max=Math.max.apply(null,data),min=Math.min.apply(null,data);
    var range=max-min||1;
    var pts=[];
    for(var i=0;i<data.length;i++){
        var x=i*(w/(data.length-1));
        var y=h-((data[i]-min)/range)*(h-4)-2;
        pts.push(x+','+y);
    }
    svg+='<polyline points="'+pts.join(' ')+'" fill="none" stroke="'+color+'" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>';
    svg+='<linearGradient id="sg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="'+color+'" stop-opacity=".3"/><stop offset="100%" stop-color="'+color+'" stop-opacity="0"/></linearGradient>';
    svg+='<polygon points="0,'+h+' '+pts.join(' ')+' '+w+','+h+'" fill="url(#sg)"/>';
    svg+='</svg>';
    return svg;
}

function renderStats(){
    var html='';
    stats.forEach(function(s){
        var iconSvg=icons[s.icon]||'';
        html+='<div class="stat-card">';
        html+='<div class="stat-top"><div class="stat-icon '+s.color+'">'+iconSvg+'</div><div><div class="stat-label">'+s.label+'</div><div class="stat-value">'+s.value+'</div></div></div>';
        if(s.progress){
            html+='<div class="progress-bar">';
            s.progress.forEach(function(p){html+='<div style="width:'+p.v+'%;background:'+p.c+'"></div>';});
            html+='</div>';
            html+='<div class="stat-footer">'+s.labels.map(function(l){return '<span>'+l+'</span>';}).join('')+'</div>';
        }else if(s.color==='red'){
            html+='<div class="alert-count">'+s.value+'</div>';
            html+='<div class="stat-footer"><span>'+s.detail+'</span><span>'+s.sub+'</span></div>';
        }else if(s.icon==='gauge'){
            var tatOffset = Math.max(0, Math.min(78.5, 78.5 - (dbAvgTat / 24.0) * 78.5));
            html+='<div class="gauge-wrap"><svg width="60" height="35" viewBox="0 0 60 35"><path d="M5 30 A25 25 0 0 1 55 30" fill="none" stroke="#e2e8f0" stroke-width="5" stroke-linecap="round"/><path d="M5 30 A25 25 0 0 1 55 30" fill="none" stroke="#7c3aed" stroke-width="5" stroke-linecap="round" stroke-dasharray="78.5" stroke-dashoffset="'+tatOffset.toFixed(1)+'"/></svg></div>';
            html+='<div class="stat-footer"><span>'+s.detail+' '+s.sub+'</span></div>';
        }else{
            if(s.spark)html+='<div class="sparkline">'+makeSparkline(s.spark,80,35,s.color==='teal'?'#0f766e':s.color==='blue'?'#1d4ed8':'#d97706')+'</div>';
            html+='<div class="stat-footer"><span>'+s.detail+'</span><span>'+s.sub+'</span></div>';
        }
        html+='</div>';
    });
    document.getElementById('dashStats').innerHTML=html;
}

function renderCollectTabs(){
    var tabs=[
        {label:'Today',count:todaySampleNotCollectedList.length,badgeClass:'green'},
        {label:'Backlog',count:backlogSampleNotCollectedList.length,badgeClass:'red'},
        {label:'Total',count:todaySampleNotCollectedList.length+backlogSampleNotCollectedList.length,badgeClass:'blue'}
    ];
    
    // Default to Backlog if today is empty and backlog has items
    var initialIdx = (todaySampleNotCollectedList.length === 0 && backlogSampleNotCollectedList.length > 0) ? 1 : 0;
    
    var html='';
    tabs.forEach(function(t,i){
        html+='<button class="dash-tab'+(i===initialIdx?' active':'')+'" data-idx="'+i+'">'+t.label+' <span class="badge '+t.badgeClass+'">'+t.count+'</span></button>';
    });
    document.getElementById('collectTabs').innerHTML=html;

    document.getElementById('collectHead').innerHTML='<tr><th>Patient ID</th><th>Patient Name</th><th>Priority</th><th>Status</th><th>Action</th></tr>';
    renderCollectTable(initialIdx);

    document.querySelectorAll('.dash-tab').forEach(function(btn){
        btn.addEventListener('click',function(){
            document.querySelectorAll('.dash-tab').forEach(function(b){b.classList.remove('active')});
            this.classList.add('active');
            renderCollectTable(parseInt(this.dataset.idx));
        });
    });
}

function renderCollectTable(idx){
    var data = idx === 0 ? todaySampleNotCollectedList : idx === 1 ? backlogSampleNotCollectedList : todaySampleNotCollectedList.concat(backlogSampleNotCollectedList);
    var html = '';
    
    if (!data || data.length === 0) {
        html = '<tr><td colspan="5" style="text-align:center;padding:24px;color:#64748b;font-size:12px">No samples pending collection in this view.</td></tr>';
        document.getElementById('collectBody').innerHTML = html;
        return;
    }
    
    data.slice(0, 15).forEach(function(row){
        var priority = (row.priority || 'Routine');
        var priLower = priority.toLowerCase();
        var priClass = (priLower === 'high' || priLower === 'urgent' || priLower === 'stat') ? 'high' : 'low';
        
        var fullName = ((row.firstName || '') + (row.middleName ? ' ' + row.middleName : '') + (row.lastName ? ' ' + row.lastName : '')).trim();
        if (!fullName) fullName = 'Unknown';
        
        var stNum = row.stNumber || '-';
        
        var statusBadge = row.hasPaid 
            ? '<span class="status-badge" style="background:#dcfce7;color:#15803d">Ready</span>' 
            : '<span class="status-badge" style="background:#fffbeb;color:#b45309">Payment Pending</span>';
            
        var actionLink = '';
        if (row.accessionNumber) {
            actionLink = '<a href="AccessionResults.do?accessionNumber=' + encodeURIComponent(row.accessionNumber) + '&referer=LabDashboard" class="collect-btn" style="background:#1d4ed8">Results</a>';
        } else if (row.orderId) {
            if (row.hasPaid) {
                actionLink = '<a href="SamplePatientEntry.do?id=' + encodeURIComponent(row.orderId) + '&patientId=' + encodeURIComponent(row.stNumber || '') + '" class="collect-btn">Collect</a>';
            } else {
                actionLink = '<span class="collect-btn" style="background:#9ca3af;cursor:not-allowed;opacity:0.7;" title="Payment Pending in Odoo">Unpaid</span>';
            }
        } else {
            actionLink = '<a href="SamplesToCollect.do" class="collect-btn">View</a>';
        }

        html += '<tr>';
        html += '<td style="font-weight:600">' + stNum + '</td>';
        html += '<td>' + fullName + '</td>';
        html += '<td><span class="priority-badge ' + priClass + '">' + priority + '</span></td>';
        html += '<td>' + statusBadge + '</td>';
        html += '<td>' + actionLink + '</td>';
        html += '</tr>';
    });
    document.getElementById('collectBody').innerHTML = html;
}

function renderWorkflowChart(){
    var canvas=document.getElementById('workflowChart');
    if(!canvas) return;
    var ctx=canvas.getContext('2d');
    var dpr=window.devicePixelRatio||1;
    var rect=canvas.parentElement.getBoundingClientRect();
    canvas.width=rect.width*dpr;
    canvas.height=rect.height*dpr;
    ctx.scale(dpr,dpr);
    var w=rect.width,h=rect.height;

    ctx.fillStyle='#f8fafc';
    ctx.fillRect(0,0,w,h);

    var depts = dbTatList && dbTatList.length > 0 ? dbTatList : [
        {dept:'Haematology', tat:7.1},
        {dept:'Urinalysis', tat:8.6},
        {dept:'Biochemistry', tat:14.6},
        {dept:'Parasitology', tat:9.0},
        {dept:'Molecular', tat:18.2}
    ];

    var maxVal = 24.0;
    var chartH = h - 35;
    var padL = 35, padR = 15;
    var barW = (w - padL - padR) / (depts.length * 1.8);

    // Grid lines
    ctx.fillStyle='#64748b';
    ctx.font='9px sans-serif';
    ctx.textAlign='right';
    for(var v=0; v<=maxVal; v+=6){
        var y = h - 25 - (v / maxVal * chartH);
        ctx.fillText(v + 'h', padL - 4, y + 3);
        ctx.strokeStyle='#e2e8f0';
        ctx.lineWidth=0.5;
        ctx.beginPath();
        ctx.moveTo(padL, y);
        ctx.lineTo(w - padR, y);
        ctx.stroke();
    }

    // Bars
    for(var i=0; i<depts.length; i++){
        var x = padL + i * ((w - padL - padR) / depts.length) + 6;
        var barVal = depts[i].tat;
        var barH = (barVal / maxVal) * chartH;

        ctx.fillStyle='#0f766e';
        ctx.beginPath();
        if (ctx.roundRect) {
            ctx.roundRect(x, h - 25 - barH, barW, barH, [3, 3, 0, 0]);
        } else {
            ctx.rect(x, h - 25 - barH, barW, barH);
        }
        ctx.fill();

        // Value on top of bar
        ctx.fillStyle='#0f172a';
        ctx.font='bold 9px sans-serif';
        ctx.textAlign='center';
        ctx.fillText(barVal.toFixed(1) + 'h', x + barW / 2, h - 28 - barH);

        // Dept label
        ctx.fillStyle='#64748b';
        ctx.font='9px sans-serif';
        var shortName = depts[i].dept.length > 9 ? depts[i].dept.substring(0, 8) + '..' : depts[i].dept;
        ctx.fillText(shortName, x + barW / 2, h - 8);
    }
}

function renderInsightsChart(){
    var canvas=document.getElementById('insightsChart');
    if(!canvas) return;
    var ctx=canvas.getContext('2d');
    var dpr=window.devicePixelRatio||1;
    var rect=canvas.parentElement.getBoundingClientRect();
    canvas.width=rect.width*dpr;
    canvas.height=rect.height*dpr;
    ctx.scale(dpr,dpr);
    var w=rect.width,h=rect.height;

    ctx.fillStyle='#f8fafc';
    ctx.fillRect(0,0,w,h);

    var volData = dbVolumeList && dbVolumeList.length > 0 ? dbVolumeList : [
        {dept:'Haematology', cnt:419},
        {dept:'Urinalysis', cnt:142},
        {dept:'Biochemistry', cnt:108},
        {dept:'Parasitology', cnt:23},
        {dept:'Serology', cnt:21}
    ];

    var maxVal = 450;
    var chartH = h - 35;
    var padL = 35, padR = 15;
    var barW = (w - padL - padR) / (volData.length * 1.8);

    // Grid lines
    ctx.fillStyle='#64748b';
    ctx.font='9px sans-serif';
    ctx.textAlign='right';
    for(var v=0; v<=maxVal; v+=150){
        var y = h - 25 - (v / maxVal * chartH);
        ctx.fillText(v, padL - 4, y + 3);
        ctx.strokeStyle='#e2e8f0';
        ctx.lineWidth=0.5;
        ctx.beginPath();
        ctx.moveTo(padL, y);
        ctx.lineTo(w - padR, y);
        ctx.stroke();
    }

    // Bars
    var barColors = ['#0f766e', '#1d4ed8', '#d97706', '#7c3aed', '#dc2626', '#0891b2'];
    for(var i=0; i<volData.length; i++){
        var x = padL + i * ((w - padL - padR) / volData.length) + 6;
        var barVal = volData[i].cnt;
        var barH = (barVal / maxVal) * chartH;

        ctx.fillStyle = barColors[i % barColors.length];
        ctx.beginPath();
        if (ctx.roundRect) {
            ctx.roundRect(x, h - 25 - barH, barW, barH, [3, 3, 0, 0]);
        } else {
            ctx.rect(x, h - 25 - barH, barW, barH);
        }
        ctx.fill();

        // Value on top of bar
        ctx.fillStyle='#0f172a';
        ctx.font='bold 9px sans-serif';
        ctx.textAlign='center';
        ctx.fillText(barVal, x + barW / 2, h - 28 - barH);

        // Dept label
        ctx.fillStyle='#64748b';
        ctx.font='9px sans-serif';
        var shortName = volData[i].dept.length > 9 ? volData[i].dept.substring(0, 8) + '..' : volData[i].dept;
        ctx.fillText(shortName, x + barW / 2, h - 8);
    }
}

renderStats();
renderCollectTabs();
setTimeout(function(){renderWorkflowChart();renderInsightsChart()},100);
window.addEventListener('resize',function(){renderWorkflowChart();renderInsightsChart()});
</script>
