<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib uri="/struts-tags" prefix="s" %>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>

<div class="stockout-panel" style="margin: 10px 0; padding: 10px; border: 1px solid #cc0000; background-color: #fff5f5;">
    <h4 style="color: #cc0000; margin: 0 0 10px 0;">
        <s:text name="stockout.void.reason"/>: <s:text name="stockout.notice.type"/>
    </h4>
    
    <div class="stockout-controls">
        <div style="margin-bottom: 10px;">
            <label><s:text name="stockout.notice.accessionNumber"/>:</label>
            <input type="text" id="stockoutAccessionNumber" name="stockoutAccessionNumber" 
                   class="stockout-input" placeholder="Enter Lab Number"/>
        </div>
        
        <div style="margin-bottom: 10px;">
            <label><s:text name="stockout.notice.affectedTests"/>:</label>
            <div id="stockoutTestList" class="stockout-test-list" style="max-height: 200px; overflow-y: auto; border: 1px solid #ccc; padding: 5px;">
                <!-- Test list will be populated dynamically -->
            </div>
        </div>
        
        <div style="margin-bottom: 10px;">
            <label><s:text name="stockout.notice.voidReason"/>:</label>
            <input type="text" id="stockoutVoidReason" name="stockoutVoidReason" 
                   class="stockout-input" value="Reagent Stock Out" readonly/>
        </div>
        
        <div class="stockout-buttons">
            <button type="button" id="stockoutSelectAll" class="btn btn-secondary" onclick="StockOutHandler.selectAllTests();">
                <s:text name="label.button.checkAll"/>
            </button>
            <button type="button" id="stockoutDeselectAll" class="btn btn-secondary" onclick="StockOutHandler.deselectAllTests();">
                <s:text name="label.button.uncheckAll"/>
            </button>
            <button type="button" id="stockoutVoidBtn" class="btn btn-danger stockout-void-btn" 
                    data-accession-number="" data-test-ids="">
                <s:text name="stockout.button.voidOrder"/>
            </button>
            <button type="button" id="stockoutPrintBtn" class="btn btn-info stockout-print-btn" 
                    data-accession-number="" style="display: none;">
                <s:text name="stockout.button.printNotice"/>
            </button>
        </div>
    </div>
</div>

<style>
.stockout-panel {
    font-family: Arial, sans-serif;
    font-size: 12px;
}

.stockout-input {
    width: 200px;
    padding: 5px;
    border: 1px solid #ccc;
    border-radius: 3px;
}

.stockout-test-list {
    width: 100%;
    min-height: 100px;
}

.stockout-test-list label {
    display: block;
    padding: 3px;
    cursor: pointer;
}

.stockout-test-list label:hover {
    background-color: #f0f0f0;
}

.stockout-buttons {
    margin-top: 10px;
}

.btn {
    padding: 5px 10px;
    margin-right: 5px;
    border: none;
    border-radius: 3px;
    cursor: pointer;
    font-size: 12px;
}

.btn-danger {
    background-color: #dc3545;
    color: white;
}

.btn-danger:hover {
    background-color: #c82333;
}

.btn-secondary {
    background-color: #6c757d;
    color: white;
}

.btn-secondary:hover {
    background-color: #545b62;
}

.btn-info {
    background-color: #17a2b8;
    color: white;
}

.btn-info:hover {
    background-color: #138496;
}
</style>

<script src="/openelis/pages/dashboard/stockOutHandler.js"></script>
