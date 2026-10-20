import sys

path = "/opt/emr/bahmni-docker/bahmni-standard/docker-compose.yml"
with open(path, "r") as f:
    content = f.read()

target = '      - "/opt/emr/openelis-custom/classes/us/mn/state/health/lims/test/action/TestSetActiveAction.class:/run/bahmni-lab/bahmni-lab/WEB-INF/classes/us/mn/state/health/lims/test/action/TestSetActiveAction.class"'

replacement = '''      - "/opt/emr/openelis-custom/classes/us/mn/state/health/lims/test/action/TestSetActiveAction.class:/run/bahmni-lab/bahmni-lab/WEB-INF/classes/us/mn/state/health/lims/test/action/TestSetActiveAction.class"
      - "/opt/emr/openelis-custom/classes/us/mn/state/health/lims/panel/action/PanelSetActiveAction.class:/run/bahmni-lab/bahmni-lab/WEB-INF/classes/us/mn/state/health/lims/panel/action/PanelSetActiveAction.class"
      - "/opt/emr/openelis-custom/classes/et:/run/bahmni-lab/bahmni-lab/WEB-INF/classes/et"
      - "/opt/emr/openelis-custom/pages/test/inactiveTests.jsp:/run/bahmni-lab/bahmni-lab/pages/test/inactiveTests.jsp"
      - "/opt/emr/openelis-custom/pages/location/labLocationList.jsp:/run/bahmni-lab/bahmni-lab/pages/location/labLocationList.jsp"
      - "/opt/emr/openelis-custom/WEB-INF/struts-globalOpenELIS.xml:/run/bahmni-lab/bahmni-lab/WEB-INF/struts-globalOpenELIS.xml"'''

if target in content and "PanelSetActiveAction" not in content:
    new_content = content.replace(target, replacement)
    with open(path, "w") as f:
        f.write(new_content)
    print("SUCCESS: Updated docker-compose.yml")
elif "PanelSetActiveAction" in content:
    print("ALREADY_PRESENT: PanelSetActiveAction already in docker-compose.yml")
else:
    print("ERROR: Target line not found in docker-compose.yml")
