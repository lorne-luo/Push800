package push800.photograph.utils;

import android.app.Activity;
import android.content.Context;
import android.telephony.TelephonyManager;

public class StaticMethod {

	public static String getPhone(Activity  context) {
		TelephonyManager tm = (TelephonyManager) context.getSystemService(Context.TELEPHONY_SERVICE);
        String deviceid = tm.getDeviceId(); 
        String tel = tm.getLine1Number(); 
        String imei =tm.getSimSerialNumber();
        String imsi =tm.getSubscriberId();
		return deviceid+"#"+tel+"#"+imei+"#"+imsi;
	}
	
	public static String getPhoneNumber(Activity  context) {
		TelephonyManager tm = (TelephonyManager) context.getSystemService(Context.TELEPHONY_SERVICE);
		String tel=tm.getLine1Number();
		if(tel.startsWith("86")){
			tel=tel.substring(2);
		}else if(tel.startsWith("+86")){
			tel=tel.substring(3);
		}
		return tel;
	}
	
	public static String getPhoneIME(Activity  context) {
		TelephonyManager tm = (TelephonyManager) context.getSystemService(Context.TELEPHONY_SERVICE);
		return tm.getSimSerialNumber();
	}
}
