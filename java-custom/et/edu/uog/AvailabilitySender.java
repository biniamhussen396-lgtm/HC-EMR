package et.edu.uog;

import java.net.URL;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONTokener;
import us.mn.state.health.lims.common.util.SystemConfiguration;

public class AvailabilitySender {
    public AvailabilitySender() {}

    public static boolean send(String conceptUuid, String state) {
        try {
            String baseUrl = SystemConfiguration.getInstance().getOpenmrsApiURL();
            String username = SystemConfiguration.getInstance().getOpenmrsUsername();
            String password = SystemConfiguration.getInstance().getOpenmrsPassword();
            String targetUrl = baseUrl + "/concept/" + conceptUuid + "/name";

            ApiRequest req = new ApiRequest(targetUrl, username, password);
            String jsonResp = req.getData();
            JSONObject root = new JSONObject(new JSONTokener(jsonResp));
            JSONArray results = root.optJSONArray("results");

            // 1. Delete all existing $active / $inactive concept names
            if (results != null) {
                for (int i = 0; i < results.length(); i++) {
                    JSONObject item = results.getJSONObject(i);
                    String display = item.optString("display", "");
                    String uuid = item.optString("uuid", "");

                    if (display.length() > 0 && display.charAt(0) == '$') {
                        try {
                            URL delUrl = new URL(targetUrl + "/" + uuid + "?purge=true");
                            req.sendData("DELETE", delUrl, "");
                            System.out.println("AvailabilitySender purged old state name " + uuid);
                        } catch (Exception ex) {
                            try {
                                URL delUrl2 = new URL(targetUrl + "/" + uuid);
                                req.sendData("DELETE", delUrl2, "");
                                System.out.println("AvailabilitySender deleted old state name " + uuid);
                            } catch (Exception ex2) {
                                System.err.println("AvailabilitySender delete error: " + ex2.getMessage());
                            }
                        }
                    }
                }
            }

            // 2. Create the desired state name ($active or $inactive)
            JSONObject payload = getState(state);
            req.postData(payload.toString());
            System.out.println("AvailabilitySender created concept name $" + state + " for concept " + conceptUuid);
            return true;
        } catch (Exception e) {
            System.err.println("AvailabilitySender error: " + e.getMessage());
            e.printStackTrace();
            return false;
        }
    }

    public static JSONObject getState(String state) {
        try {
            JSONObject obj = new JSONObject();
            obj.put("name", "$" + state);
            obj.put("locale", "en");
            obj.put("localePreferred", false);
            obj.put("conceptNameType", JSONObject.NULL);
            return obj;
        } catch (JSONException e) {
            throw new RuntimeException(e);
        }
    }
}
