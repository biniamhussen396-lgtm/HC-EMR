import urllib.request
import json
from test_desync import simple_websocket_eval

r = urllib.request.urlopen('http://localhost:9222/json')
target = [p for p in json.loads(r.read().decode()) if 'appointments' in p.get('url', '')][0]

code = """
(function() {
    var tr = document.querySelector('.app-list-view table tbody tr');
    var scope = window.angular ? window.angular.element(tr).scope() : null;
    return {
        hasScope: !!scope,
        apptUuid: (scope && scope.appointment) ? scope.appointment.uuid : null,
        patientName: (scope && scope.appointment && scope.appointment.patient) ? scope.appointment.patient.name : null,
        parentHasSelect: (scope && scope.$parent && typeof scope.$parent.select === 'function') ? true : false
    };
})()
"""
res = simple_websocket_eval(target['webSocketDebuggerUrl'], code)
print(json.dumps(res, indent=2))
