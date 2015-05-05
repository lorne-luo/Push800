package push800.photograph.login;

//import java.io.InputStream;
//import java.io.InputStreamReader;
import java.io.StringReader;

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONTokener;

public class JsonLogin {
	public void parseJason(String jsonData) {
		// public void parseJason(InputStream in){
		try {
			// 如果需要解析JSON数据，首先要生成一个JsonReader对象
			//JsonReader reader = new JsonReader(new StringReader(jsonData));
			// JsonReader reader = new JsonReader(new InputStreamReader(in ,
			// "UTF-8"));
			/*
			reader.beginObject();
			while (reader.hasNext()) {
				String tagName = reader.nextName();
				if (tagName.equals("user_token"))
					System.out.println("user_token---> " + reader.nextString());
				else if (tagName.equals("success"))
					System.out.println("success---> " + reader.nextBoolean());
				else{
					System.out.println("error");
					System.out.println("error---> " + reader.nextString());
				}
			}
			reader.endObject();
			*/
			
			JSONObject obj=new JSONObject(jsonData);
			boolean success=obj.getBoolean("success");
			System.out.println("success--->" + String.valueOf(success));
			
			if (!success){
				JSONArray error = obj.getJSONArray("error");
				for (int i = 0; i < error.length(); i++) {
					System.out.println("error--->" + error.getString(i));
				}
			}else{
				System.out.println("user_token---> " + obj.get("user_token").toString());
			}
			
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
}
