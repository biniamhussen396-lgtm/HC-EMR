import json
from ws_utils import simple_websocket_eval, get_target_ws_url

ws_url = get_target_ws_url()
expr = """
(function() {
    var el = document.querySelector('[ng-app]');
    if (!el) return { error: 'no ng-app' };
    var inj = window.angular ? angular.element(el).injector() : null;
    if (!inj) return { error: 'no injector' };
    var tc = inj.get('$templateCache');
    var c1 = tc.get('views/bedManagement.html');
    var c2 = tc.get('views/bedManagement.html?v=3.4');
    var state = inj.get('$state');
    return {
        currentState: state ? state.current.name : null,
        hasC1: !!c1,
        c1HasBtn: c1 ? c1.indexOf('btn-admitted-table-view') !== -1 : false,
        hasC2: !!c2,
        c2HasBtn: c2 ? c2.indexOf('btn-admitted-table-view') !== -1 : false
    };
})()
"""

res = simple_websocket_eval(ws_url, expr)
print(json.dumps(res, indent=2))
