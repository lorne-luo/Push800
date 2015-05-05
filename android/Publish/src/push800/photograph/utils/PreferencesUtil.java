package push800.photograph.utils;

import push800.photograph.launcher.LauncherUI;
import push800.photograph.launcher.SelectCityUI;
import android.R.integer;
import android.content.Context;
import android.content.SharedPreferences;
import android.preference.PreferenceManager;

/**
 * @author Leo
 * 对Preference的设置
 */
public class PreferencesUtil {

	//---------int--------
	/**
	 * @param key 键名
	 * @param defValue 若不存在key键名，返回的缺省值
	 * @param context activity实例即可
	 * @return
	 */
	public static int getInt(String key, int defValue, Context context) {
		SharedPreferences perferences = PreferenceManager
				.getDefaultSharedPreferences(context);
		return perferences.getInt(key, defValue);
	}

	public static void putInt(String key, int value, Context context) {
		SharedPreferences perferences = PreferenceManager
				.getDefaultSharedPreferences(context);
		SharedPreferences.Editor editor = perferences.edit();
		editor.putInt(key, value);
		editor.commit();// 提交保存
	}
	
	//---------string--------
	public static String getString(String key, String defValue, Context context) {
		SharedPreferences perferences = PreferenceManager
				.getDefaultSharedPreferences(context);
		return perferences.getString(key, defValue);
	}

	public static void putString(String key, String value, Context context) {
		SharedPreferences perferences = PreferenceManager
				.getDefaultSharedPreferences(context);
		SharedPreferences.Editor editor = perferences.edit();
		editor.putString(key, value);
		editor.commit();// 提交保存
	}
}
