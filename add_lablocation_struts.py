with open("/tmp/struts-globalOpenELIS.xml", "r") as f:
    c = f.read()
target = "<action-mappings>"
addition = '\n        <action path="/LabLocationList" forward="/pages/location/labLocationList.jsp"/>'
if "/LabLocationList" not in c:
    c = c.replace(target, target + addition, 1)
    with open("/tmp/struts-globalOpenELIS.xml", "w") as f:
        f.write(c)
    print("SUCCESS: added LabLocationList")
else:
    print("ALREADY PRESENT")
