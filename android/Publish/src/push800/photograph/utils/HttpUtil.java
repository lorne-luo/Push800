package push800.photograph.utils;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.List;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.NameValuePair;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.message.BasicNameValuePair;
import org.json.JSONException;
import org.json.JSONObject;
import android.R.integer;
import android.os.Message;
import android.util.Log;

/**
 * 封装HTTP常用的post和get操作
 * 
 * @author Leo
 */
public class HttpUtil {
	private static String TAG = "HttpUtil";

	public static String Get(String url) {
		DefaultHttpClient httpClient = new DefaultHttpClient();
		HttpGet httpGet = new HttpGet(url);
		StringBuffer data = new StringBuffer();
		int statusCode = 0;
		try {
			HttpResponse response = httpClient.execute(httpGet);
			statusCode = response.getStatusLine().getStatusCode();
			if (statusCode == 200) {
				InputStream in = response.getEntity().getContent();

				BufferedReader br = new BufferedReader(new InputStreamReader(
						in, "utf-8"));
				String line = br.readLine();

				while (line != null) {
					data.append(line + "\n");// 一行一行读取
					line = br.readLine();
				}
				br.close();
				in.close();
			}
		} catch (ClientProtocolException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			httpClient.getConnectionManager().shutdown();
		}
		return data.toString();
	}

	// post一个键值对到指定的url，得到一个JSONObject
	public static JSONObject Post(String url, List<NameValuePair> param) {

		// 使用Http客户端发送请求对象
		StringBuffer data = new StringBuffer();
		try {

			HttpEntity httpEntity = new UrlEncodedFormEntity(param);
			HttpPost post = new HttpPost(url);
			post.setEntity(httpEntity);
			HttpClient httpClient = new DefaultHttpClient();
			InputStream inputStream = null;

			HttpResponse httpResponse = httpClient.execute(post);
			httpEntity = httpResponse.getEntity();
			inputStream = httpEntity.getContent();
			BufferedReader reader = new BufferedReader(new InputStreamReader(
					inputStream));
			String line = "";
			while ((line = reader.readLine()) != null) {
				data.append(line);
			}
			httpClient.getConnectionManager().shutdown();
		} catch (Exception e) {
			Log.v(TAG, "Error=" + e.getMessage());
		} 
		try {
			return new JSONObject(data.toString());
		} catch (JSONException e) {
			Log.v(TAG, "data="+data.toString());
			Log.v(TAG, "Error="+e.getMessage());
			return null;
		}
	}
	
	
}
