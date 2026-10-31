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

<!-- Stock-Out Management Panel -->
<style>
#stockoutPanel{display:none;background:#fff5f5;border:2px solid #dc2626;border-radius:8px;padding:15px;margin-top:15px}
#stockoutPanel.show{display:block}
.stockout-title{color:#dc2626;font-size:16px;font-weight:700;margin:0 0 10px 0}
.stockout-test-list{background:#fff;border:1px solid #e2e8f0;border-radius:5px;padding:10px;max-height:300px;overflow-y:auto;margin:10px 0}
.stockout-test-item{display:flex;justify-content:space-between;align-items:center;padding:8px;border-bottom:1px solid #f1f5f9}
.stockout-test-item:last-child{border-bottom:none}
.stockout-test-name{font-weight:600;font-size:12px;color:#1a1a2e}
.stockout-test-type{font-size:11px;color:#64748b}
.stockout-toggle{display:flex;gap:5px}
.stockout-btn{padding:5px 12px;border:none;border-radius:4px;cursor:pointer;font-size:11px;font-weight:600}
.stockout-btn.available{background:#dcfce7;color:#16a34a;border:1px solid #16a34a}
.stockout-btn.available:hover{background:#bbf7d0}
.stockout-btn.stockout{background:#fee2e2;color:#dc2626;border:1px solid #dc2626}
.stockout-btn.stockout:hover{background:#fecaca}
.stockout-btn.selected{box-shadow:0 0 0 2px currentColor}
.stockout-actions{display:flex;gap:10px;margin-top:15px;justify-content:flex-end}
.stockout-actions .btn{padding:8px 20px;border:none;border-radius:5px;cursor:pointer;font-size:12px;font-weight:500}
.stockout-actions .btn-danger{background:#dc2626;color:#fff}
.stockout-actions .btn-danger:hover{background:#b91c1c}
.stockout-actions .btn-secondary{background:#e2e8f0;color:#334155}
.stockout-actions .btn-secondary:hover{background:#cbd5e1}
.stockout-actions .btn-success{background:#16a34a;color:#fff}
.stockout-actions .btn-success:hover{background:#15803d}
.stockout-notice-modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:1000;justify-content:center;align-items:center}
.stockout-notice-modal.show{display:flex}
.stockout-notice-dialog{background:#fff;border-radius:8px;padding:20px;width:90%;max-width:500px;max-height:80vh;overflow-y:auto}
.stockout-notice-dialog h3{color:#dc2626;margin:0 0 15px 0;font-size:16px}
.stockout-notice-dialog .close-btn{float:right;background:none;border:none;font-size:20px;cursor:pointer;color:#64748b}
.stockout-notice-dialog .btn-row{display:flex;gap:10px;margin-top:15px;justify-content:flex-end}
.stockout-notice-dialog .btn{padding:8px 16px;border:none;border-radius:5px;cursor:pointer;font-size:12px;font-weight:500}
.stockout-notice-dialog .btn-danger{background:#dc2626;color:#fff}
.stockout-notice-dialog .btn-danger:hover{background:#b91c1c}
.stockout-notice-dialog .btn-secondary{background:#e2e8f0;color:#334155}
.stockout-notice-dialog .btn-secondary:hover{background:#cbd5e1}
.stockout-notice-dialog .order-info{background:#f8fafc;padding:10px;border-radius:5px;margin-bottom:15px;font-size:12px}
.stockout-notice-dialog .order-info strong{color:#0f172a}
.stockout-info{font-size:11px;color:#64748b;margin:5px 0}
</style>

<div id="stockoutPanel">
    <div style="display:flex;justify-content:space-between;align-items:center">
        <p class="stockout-title">Stock-Out Management</p>
        <button onclick="StockOut.hidePanel()" style="background:none;border:none;font-size:16px;cursor:pointer;color:#64748b">&times;</button>
    </div>
    <p class="stockout-info">Mark tests as Stock-Out for unavailable reagents. Available tests will proceed normally.</p>
    <div id="stockoutTestList" class="stockout-test-list">
        <p style="color:#64748b;font-size:12px">Loading...</p>
    </div>
    <div class="stockout-actions">
        <button class="btn btn-secondary" onclick="StockOut.markAllAvailable()">Mark All Available</button>
        <button class="btn btn-danger" onclick="StockOut.markAllStockOut()">Mark All Stock-Out</button>
        <button class="btn btn-success" onclick="StockOut.generateNotice()">Generate Stock-Out Notice</button>
    </div>
</div>

<div id="stockoutNoticeModal" class="stockout-notice-modal">
    <div class="stockout-notice-dialog">
        <button class="close-btn" onclick="StockOut.closeNoticeModal()">&times;</button>
        <h3>Stock-Out Notice Generated</h3>
        <div class="order-info">
            <strong>Notice Number:</strong> <span id="snNoticeNumber">-</span><br>
            <strong>Date:</strong> <span id="snDate">-</span><br>
            <strong>Order:</strong> <span id="snOrder">-</span><br>
            <strong>Tests Voided:</strong> <span id="snTestsVoided">-</span>
        </div>
        <p style="font-size:12px;color:#64748b">The stock-out notice has been sent to print. The billing team has been notified via Odoo sync.</p>
        <div class="btn-row">
            <button class="btn btn-secondary" onclick="StockOut.closeNoticeModal()">Close</button>
        </div>
    </div>
</div>

<script>
var StockOut={
    tests:[],
    selectedStatus:{},
    currentOrderId:null,

    showPanel:function(orderId, tests){
        this.currentOrderId=orderId;
        this.tests=tests||[];
        this.selectedStatus={};

        if(this.tests.length===0){
            this.tests=[{testName:'All Tests in Order',testType:'N/A',testId:orderId}];
        }

        var html='';
        this.tests.forEach(function(t,i){
            var name=t.testName||('Test '+(i+1));
            var type=t.testType||t.testCode||'';
            html+='<div class="stockout-test-item">';
            html+='<div><div class="stockout-test-name">'+name+'</div>';
            html+='<div class="stockout-test-type">'+type+'</div></div>';
            html+='<div class="stockout-toggle">';
            html+='<button class="stockout-btn available" id="so-avail-'+i+'" onclick="StockOut.setStatus('+i+',\'available\')">Available</button>';
            html+='<button class="stockout-btn stockout" id="so-so-'+i+'" onclick="StockOut.setStatus('+i+',\'stockout\')">Stock-Out</button>';
            html+='</div></div>';
        });
        document.getElementById('stockoutTestList').innerHTML=html;
        document.getElementById('stockoutPanel').classList.add('show');
    },

    hidePanel:function(){
        document.getElementById('stockoutPanel').classList.remove('show');
    },

    setStatus:function(index,status){
        this.selectedStatus[index]=status;
        var availBtn=document.getElementById('so-avail-'+index);
        var soBtn=document.getElementById('so-so-'+index);
        if(availBtn)availBtn.classList.remove('selected');
        if(soBtn)soBtn.classList.remove('selected');
        if(status==='available'){
            if(availBtn)availBtn.classList.add('selected');
        }else{
            if(soBtn)soBtn.classList.add('selected');
        }
    },

    markAllAvailable:function(){
        var self=this;
        this.tests.forEach(function(t,i){self.setStatus(i,'available')});
    },

    markAllStockOut:function(){
        var self=this;
        this.tests.forEach(function(t,i){self.setStatus(i,'stockout')});
    },

    getStockOutTests:function(){
        var self=this;
        var result=[];
        this.tests.forEach(function(t,i){
            if(self.selectedStatus[i]==='stockout'){
                result.push(t.testName||('Test '+(i+1)));
            }
        });
        return result;
    },

    generateNotice:function(){
        var self=this;
        var stockOutTests=this.getStockOutTests();
        if(stockOutTests.length===0){
            alert('Please mark at least one test as Stock-Out before generating a notice.');
            return;
        }

        var noticeNumber='SO-'+Date.now().toString(36).toUpperCase();
        var noticeDate=new Date().toLocaleString();
        var order=this.currentOrderId;

        var printContent='<!DOCTYPE html><html><head><title>Stock-Out Notice</title>';
        printContent+='<style>';
        printContent+='body{font-family:Arial,sans-serif;margin:20px;font-size:12px;line-height:1.5}';
        printContent+='h1{font-size:18px;text-align:center;border-bottom:2px solid #000;padding-bottom:10px;margin-bottom:5px}';
        printContent+='h2{font-size:14px;text-align:center;color:#dc2626;margin:5px 0 15px 0}';
        printContent+='table{width:100%;border-collapse:collapse;margin:15px 0}';
        printContent+='td{border:1px solid #ccc;padding:8px;font-size:11px}';
        printContent+='td:first-child{background:#f5f5f5;font-weight:bold;width:30%}';
        printContent+='h3{color:#dc2626;border-bottom:1px solid #dc2626;padding-bottom:5px;font-size:14px}';
        printContent+='.action-box{border:2px solid #dc2626;padding:15px;margin:15px 0;background:#fff5f5}';
        printContent+='.action-box ol{margin:10px 0;padding-left:20px}';
        printContent+='.action-box li{margin:5px 0}';
        printContent+='.sig-section{display:flex;justify-content:space-between;margin-top:40px}';
        printContent+='.sig-box{width:45%;border-top:1px solid #000;padding-top:5px}';
        printContent+='.footer{text-align:center;font-size:10px;color:#666;margin-top:20px}';
        printContent+='@media print{body{margin:10px}}';
        printContent+='</style></head><body>';
        printContent+='<h1>LABORATORY STOCK-OUT NOTICE</h1>';
        printContent+='<h2>Non-Conformity Report for Reagent Unavailability</h2>';
        printContent+='<table>';
        printContent+='<tr><td>Notice Number:</td><td><strong>'+noticeNumber+'</strong></td><td>Date:</td><td><strong>'+noticeDate+'</strong></td></tr>';
        if(order){printContent+='<tr><td>Order ID:</td><td colspan="3">'+order+'</td></tr>';}
        printContent+='</table>';
        printContent+='<h3>Affected Tests (Cancelled)</h3>';
        printContent+='<table><tr><td colspan="4" style="background:#f8fafc;font-weight:bold">Tests marked as Stock-Out due to reagent unavailability.</td></tr>';
        stockOutTests.forEach(function(t){
            printContent+='<tr><td>'+t+'</td><td>Reagent Stock Out</td><td>'+noticeDate+'</td><td>Cancelled</td></tr>';
        });
        printContent+='</table>';
        printContent+='<div class="action-box"><strong>Required Actions:</strong><ol>';
        printContent+='<li>Notify the ordering clinician about the reagent stock-out</li>';
        printContent+='<li>Advise patient to return when reagents are available</li>';
        printContent+='<li>Schedule follow-up appointment if clinically urgent</li>';
        printContent+='<li>Update inventory system with stock-out record</li>';
        printContent+='</ol></div>';
        printContent+='<div class="sig-section"><div class="sig-box"><p>Receptionist Signature</p></div>';
        printContent+='<div class="sig-box"><p>Patient/Guardian Signature</p></div></div>';
        printContent+='<div class="footer"><p>This notice confirms that the above test(s) could not be performed due to reagent unavailability.</p>';
        printContent+='<p>Please retain this notice for your records and follow up with your clinician.</p></div>';
        printContent+='</body></html>';

        var w=window.open('','StockOutNotice','width=800,height=600,scrollbars=yes');
        if(w){w.document.write(printContent);w.document.close();setTimeout(function(){w.print()},500);}

        document.getElementById('snNoticeNumber').textContent=noticeNumber;
        document.getElementById('snDate').textContent=noticeDate;
        document.getElementById('snOrder').textContent=order||'N/A';
        document.getElementById('snTestsVoided').textContent=stockOutTests.join(', ');
        document.getElementById('stockoutNoticeModal').classList.add('show');
        this.hidePanel();
    },

    closeNoticeModal:function(){
        document.getElementById('stockoutNoticeModal').classList.remove('show');
    }
};
</script>
