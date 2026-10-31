/**
 * Stock-Out Notice JavaScript Handler
 * Handles order voiding and stock-out notice generation in OpenELIS
 */

var StockOutHandler = {
    /**
     * Initialize stock-out functionality
     */
    init: function() {
        this.bindEvents();
    },

    /**
     * Bind event handlers
     */
    bindEvents: function() {
        $(document).on('click', '.stockout-void-btn', this.handleVoidOrder.bind(this));
        $(document).on('click', '.stockout-print-btn', this.handlePrintNotice.bind(this));
    },

    /**
     * Handle void order button click
     */
    handleVoidOrder: function(e) {
        e.preventDefault();
        var btn = $(e.currentTarget);
        var accessionNumber = btn.data('accession-number');
        var testIds = btn.data('test-ids');

        if (!accessionNumber) {
            alert('Accession number is required');
            return;
        }

        // Show confirmation dialog
        if (!confirm('Are you sure you want to void this order due to Reagent Stock Out?')) {
            return;
        }

        // Collect voided test IDs
        var voidedTestIds = [];
        $('input[name="voidTest"]:checked').each(function() {
            voidedTestIds.push($(this).val());
        });

        if (voidedTestIds.length === 0) {
            alert('Please select at least one test to void');
            return;
        }

        // Call API to void order and generate notice
        this.voidOrder(accessionNumber, voidedTestIds);
    },

    /**
     * Void order via API
     */
    voidOrder: function(accessionNumber, testIds) {
        var self = this;
        
        $.ajax({
            url: '/openelis/StockOutNoticeAPI.do',
            type: 'POST',
            data: {
                action: 'generateNotice',
                accessionNumber: accessionNumber,
                'voidedTestIds[]': testIds,
                voidReason: 'Reagent Stock Out'
            },
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    self.showSuccessMessage(response);
                    self.openPrintWindow(response);
                    // Refresh the page or update UI
                    location.reload();
                } else {
                    alert('Error: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                alert('Error voiding order: ' + error);
            }
        });
    },

    /**
     * Show success message
     */
    showSuccessMessage: function(response) {
        var message = 'Order voided successfully!\n\n';
        message += 'Notice Number: ' + response.noticeNumber + '\n';
        message += 'Patient: ' + response.patientName + '\n';
        message += 'Accession: ' + response.accessionNumber;
        alert(message);
    },

    /**
     * Open print window for stock-out notice
     */
    openPrintWindow: function(response) {
        var printUrl = '/openelis/StockOutNotice.do?accessionNumber=' + response.accessionNumber;
        window.open(printUrl, 'StockOutNotice', 'width=800,height=600,scrollbars=yes');
    },

    /**
     * Handle print notice button click
     */
    handlePrintNotice: function(e) {
        e.preventDefault();
        var btn = $(e.currentTarget);
        var accessionNumber = btn.data('accession-number');
        
        if (accessionNumber) {
            var printUrl = '/openelis/StockOutNotice.do?accessionNumber=' + accessionNumber;
            window.open(printUrl, 'StockOutNotice', 'width=800,height=600,scrollbars=yes');
        }
    },

    /**
     * Select all tests for voiding
     */
    selectAllTests: function() {
        $('input[name="voidTest"]').prop('checked', true);
    },

    /**
     * Deselect all tests
     */
    deselectAllTests: function() {
        $('input[name="voidTest"]').prop('checked', false);
    }
};

// Initialize when document is ready
$(document).ready(function() {
    StockOutHandler.init();
});
