<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib uri="/struts-tags" prefix="s" %>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Stock-Out Notice</title>
    <style>
        @media print {
            body { margin: 0; }
            .no-print { display: none; }
        }
        body {
            font-family: Arial, sans-serif;
            font-size: 12px;
            margin: 20px;
        }
        .header {
            text-align: center;
            border-bottom: 2px solid #000;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .header h1 {
            font-size: 18px;
            margin: 5px 0;
        }
        .header h2 {
            font-size: 14px;
            margin: 5px 0;
            color: #cc0000;
        }
        .notice-type {
            text-align: center;
            font-size: 16px;
            font-weight: bold;
            color: #cc0000;
            border: 2px solid #cc0000;
            padding: 5px;
            margin: 10px 0;
        }
        .info-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        .info-table td {
            padding: 5px 10px;
            border: 1px solid #ccc;
        }
        .info-table td:first-child {
            font-weight: bold;
            width: 30%;
            background-color: #f5f5f5;
        }
        .items-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        .items-table th, .items-table td {
            border: 1px solid #000;
            padding: 8px;
            text-align: left;
        }
        .items-table th {
            background-color: #333;
            color: white;
        }
        .items-table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .reason-box {
            border: 1px solid #cc0000;
            padding: 10px;
            margin: 15px 0;
            background-color: #fff0f0;
        }
        .reason-box h3 {
            margin-top: 0;
            color: #cc0000;
        }
        .signature-section {
            margin-top: 30px;
            display: flex;
            justify-content: space-between;
        }
        .signature-box {
            width: 45%;
            border-top: 1px solid #000;
            padding-top: 5px;
            margin-top: 50px;
        }
        .footer {
            margin-top: 20px;
            font-size: 10px;
            text-align: center;
            color: #666;
        }
        .print-btn {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            cursor: pointer;
            font-size: 14px;
            margin: 10px;
        }
        .close-btn {
            background-color: #f44336;
            color: white;
            padding: 10px 20px;
            border: none;
            cursor: pointer;
            font-size: 14px;
            margin: 10px;
        }
    </style>
</head>
<body>
    <div class="no-print" style="text-align: center; margin-bottom: 20px;">
        <button class="print-btn" onclick="window.print()">Print Notice</button>
        <button class="close-btn" onclick="window.close()">Close</button>
    </div>

    <div class="header">
        <h1><s:text name="stockout.notice.facilityName"/></h1>
        <h2><s:text name="stockout.notice.title"/></h2>
        <p><s:text name="stockout.notice.subtitle"/></p>
    </div>

    <div class="notice-type">
        <s:text name="stockout.notice.type"/>
    </div>

    <table class="info-table">
        <tr>
            <td><s:text name="stockout.notice.noticeNumber"/>:</td>
            <td><s:property value="noticeNumber"/></td>
            <td><s:text name="stockout.notice.date"/>:</td>
            <td><s:property value="noticeDate"/></td>
        </tr>
        <tr>
            <td><s:text name="stockout.notice.patientName"/>:</td>
            <td><s:property value="patientName"/></td>
            <td><s:text name="stockout.notice.patientId"/>:</td>
            <td><s:property value="patientId"/></td>
        </tr>
        <tr>
            <td><s:text name="stockout.notice.accessionNumber"/>:</td>
            <td><s:property value="accessionNumber"/></td>
            <td><s:text name="stockout.notice.receptionist"/>:</td>
            <td><s:property value="receptionistName"/></td>
        </tr>
        <tr>
            <td><s:text name="stockout.notice.orderingClinician"/>:</td>
            <td colspan="3"><s:property value="orderingClinician"/></td>
        </tr>
    </table>

    <h3><s:text name="stockout.notice.affectedTests"/></h3>
    <table class="items-table">
        <thead>
            <tr>
                <th><s:text name="stockout.notice.testName"/></th>
                <th><s:text name="stockout.notice.testCode"/></th>
                <th><s:text name="stockout.notice.sampleType"/></th>
                <th><s:text name="stockout.notice.voidReason"/></th>
                <th><s:text name="stockout.notice.voidTime"/></th>
            </tr>
        </thead>
        <tbody>
            <s:iterator value="voidedTests">
                <tr>
                    <td><s:property value="testName"/></td>
                    <td><s:property value="testCode"/></td>
                    <td><s:property value="sampleType"/></td>
                    <td><s:property value="voidReason"/></td>
                    <td><s:property value="voidTime"/></td>
                </tr>
            </s:iterator>
        </tbody>
    </table>

    <div class="reason-box">
        <h3><s:text name="stockout.notice.actionRequired"/></h3>
        <p><s:text name="stockout.notice.actionDescription"/></p>
        <ol>
            <li><s:text name="stockout.notice.action1"/></li>
            <li><s:text name="stockout.notice.action2"/></li>
            <li><s:text name="stockout.notice.action3"/></li>
        </ol>
    </div>

    <div class="signature-section">
        <div class="signature-box">
            <p><s:text name="stockout.notice.receptionistSignature"/></p>
        </div>
        <div class="signature-box">
            <p><s:text name="stockout.notice.patientSignature"/></p>
        </div>
    </div>

    <div class="footer">
        <p><s:text name="stockout.notice.footer1"/></p>
        <p><s:text name="stockout.notice.footer2"/></p>
    </div>
</body>
</html>
