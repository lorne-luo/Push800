package push800.photograph.utils;

import java.util.ArrayList;

import android.R.string;
import android.util.Log;

/*
 * 所有与服务器所有交互的url都写在这里
 */
public class City {

	public static String[] CITY_NAME_LIST = new String[]{"不限","北京","上海","广州","深圳","天津"};
	public static String[] CITY_SHORTNAME_LIST = new String[]{"","bj","sh","gz","sz","tj"};

	public static String getShortName(String cityName) {
		for (int i = 0; i < City.CITY_NAME_LIST.length; i++) {
			if (cityName.equals(City.CITY_NAME_LIST[i])) {
				//找到了此城市名，返回对应的拼音缩写
				
				return City.CITY_SHORTNAME_LIST[i];
			}
		}
		//没找到则返回不限
		return City.CITY_SHORTNAME_LIST[0];
	}
	
	public static int getIDByName(String cityName) {
		for (int i = 0; i < City.CITY_NAME_LIST.length; i++) {
			if (cityName.equals(City.CITY_NAME_LIST[i])) {
				return i;//找到了此城市名，返回对应的ID
			}
		}
		
		return 0;//没找到则返回0
	}

	public static String getShortNameByID(int cityID) {
		return City.CITY_SHORTNAME_LIST[cityID];
	}

	public static String getNameByID(int cityID) {
		return City.CITY_NAME_LIST[cityID];
	}
}
