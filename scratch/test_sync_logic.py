import urllib.request
import json
from test_desync import simple_websocket_eval

r = urllib.request.urlopen('http://localhost:9222/json')
target = [p for p in json.loads(r.read().decode()) if 'appointments' in p.get('url', '')][0]
ws_url = target['webSocketDebuggerUrl']

code = """
(function() {
    var table = document.querySelector('.app-list-view table');
    var tbody = table ? table.querySelector('tbody') : null;
    var tr = tbody ? tbody.querySelector('tr') : null;
    if (!tr) return { error: 'No tr found' };

    var childScope = window.angular.element(tr).scope();
    var parentScope = childScope ? childScope.$parent : null;
    if (!parentScope) return { error: 'No parentScope' };

    // Function to safely apply
    function safeApply(scope) {
        if (!scope.$$phase && !scope.$root.$$phase) {
            scope.$apply();
        }
    }

    // Test 1: Checkbox click with stopPropagation and scope sync
    var cb = tr.querySelector('.row-cb');
    parentScope.selectedAppointment = null;
    safeApply(parentScope);
    cb.checked = false;

    // Simulate improved checkbox click
    cb.checked = true;
    parentScope.selectedAppointment = childScope.appointment;
    safeApply(parentScope);

    var res1 = {
        cbChecked: cb.checked,
        selectedAppointmentUuid: parentScope.selectedAppointment ? parentScope.selectedAppointment.uuid : null,
        fieldsetDisabled: document.querySelector('.appointment-action-btn-container').disabled,
        isEditDisabled: document.querySelector('.appointment-action-btn-container button:nth-of-type(3)') ? document.querySelector('.appointment-action-btn-container button:nth-of-type(3)').disabled : null
    };

    // Test 2: Uncheck
    cb.checked = false;
    parentScope.selectedAppointment = undefined;
    safeApply(parentScope);

    var res2 = {
        cbChecked: cb.checked,
        selectedAppointmentUuid: parentScope.selectedAppointment ? parentScope.selectedAppointment.uuid : null,
        fieldsetDisabled: document.querySelector('.appointment-action-btn-container').disabled
    };

    return { res1: res1, res2: res2 };
})()
"""

res = simple_websocket_eval(ws_url, code)
print(json.dumps(res, indent=2))
