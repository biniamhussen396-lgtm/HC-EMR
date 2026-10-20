package et.edu.uog;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.security.KeyManagementException;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.security.cert.CertificateException;
import java.security.cert.X509Certificate;
import javax.net.ssl.HostnameVerifier;
import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSession;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509ExtendedTrustManager;
import javax.xml.bind.DatatypeConverter;

public class ApiRequest {
    private URL url;
    private String username;
    private String password;
    private static boolean is_ssl_disabled = false;

    public ApiRequest(String url) throws MalformedURLException {
        this.url = new URL(url);
    }

    public ApiRequest(String url, String username, String password) throws MalformedURLException {
        this.url = new URL(url);
        this.username = username;
        this.password = password;
    }

    public String postData(String data) throws IOException {
        return sendData("POST", this.url, data);
    }

    public String postData(String data, URL url) throws IOException {
        return sendData("POST", url, data);
    }

    public String getData() throws IOException {
        return sendData("GET", this.url, "");
    }

    public String getData(URL url) throws IOException {
        return sendData("GET", url, "");
    }

    public String deleteData(URL url) throws IOException {
        return sendData("DELETE", url, "");
    }

    public String sendData(String method, URL url, String data) throws IOException {
        HttpURLConnection connection = (HttpURLConnection) url.openConnection();
        if ("POST".equalsIgnoreCase(method) || "PUT".equalsIgnoreCase(method)) {
            connection.setDoOutput(true);
        }
        connection.setRequestMethod(method);

        if (this.username != null && this.password != null) {
            String auth = this.username + ":" + this.password;
            String encoded = DatatypeConverter.printBase64Binary(auth.getBytes("UTF-8"));
            connection.setRequestProperty("Authorization", "Basic " + encoded);
        }
        connection.setRequestProperty("Accept", "application/json");
        connection.setRequestProperty("Content-Type", "application/json");

        connection.connect();

        if (data != null && !data.isEmpty()) {
            BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(connection.getOutputStream(), "UTF-8"));
            writer.write(data);
            writer.close();
        }

        int statusCode = connection.getResponseCode();
        if (statusCode >= 200 && statusCode < 300) {
            if (statusCode == 204) {
                return "";
            }
            InputStream is = connection.getInputStream();
            if (is == null) {
                return "";
            }
            BufferedReader reader = new BufferedReader(new InputStreamReader(is, "UTF-8"));
            StringBuilder builder = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                builder.append(line);
            }
            reader.close();
            return builder.toString();
        } else {
            throw new IOException("Unexpected Status code : " + statusCode);
        }
    }

    public static void disableSSl() throws NoSuchAlgorithmException, KeyManagementException {
        if (!is_ssl_disabled) {
            is_ssl_disabled = true;
            TrustManager[] trustAllCerts = new TrustManager[] {
                new X509ExtendedTrustManager() {
                    public X509Certificate[] getAcceptedIssuers() { return null; }
                    public void checkClientTrusted(X509Certificate[] certs, String authType) {}
                    public void checkServerTrusted(X509Certificate[] certs, String authType) {}
                    public void checkClientTrusted(X509Certificate[] certs, String authType, java.net.Socket socket) {}
                    public void checkServerTrusted(X509Certificate[] certs, String authType, java.net.Socket socket) {}
                    public void checkClientTrusted(X509Certificate[] certs, String authType, javax.net.ssl.SSLEngine engine) {}
                    public void checkServerTrusted(X509Certificate[] certs, String authType, javax.net.ssl.SSLEngine engine) {}
                }
            };
            SSLContext sc = SSLContext.getInstance("SSL");
            sc.init(null, trustAllCerts, new SecureRandom());
            HttpsURLConnection.setDefaultSSLSocketFactory(sc.getSocketFactory());
            HttpsURLConnection.setDefaultHostnameVerifier(new HostnameVerifier() {
                public boolean verify(String hostname, SSLSession session) { return true; }
            });
        }
    }
}
