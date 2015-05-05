package push800.photograph.utils;

/*
 * 所有与服务器所有交互的url都写在这里
 * 必须通过public方法来获取
 */
public class Urls {
	
	private static String BASE_URL = "http://push800.sinaapp.com/";
	
	//与注册登陆提交订阅相关
	private static String REGISTER_URL = "frontserver/register/";
	private static String LOGIN_URL = "frontserver/login/";
	
	private static String SEARCH_URL = "/adv_search";
	
	private static String SUBMIT_SUBSCRIBE_URL = "frontserver/create_subscribe/";//提交订阅
	private static String USERCENTER_URL = "frontserver/subscribe_list/1/";//展示订阅list
	//与展示订阅，信息相关
	private static String CITY_HOME_URL = "pe/";
	private static String POLL_SERVICE_URL = "frontserver/subscribe_list/1/";//进行poll查询的地址
	
	/**************************************************************************************/
	
	public static String REGISTER() {
		return BASE_URL+REGISTER_URL;
	}
	public static String LOGIN() {
		return BASE_URL+LOGIN_URL;
	}
	public static String SUBMIT_SUBSCRIBE() {
		return BASE_URL+SUBMIT_SUBSCRIBE_URL;
	}
	public static String USERCENTER() {
		return BASE_URL+USERCENTER_URL;
	}
	public static String CITY_HOME() {
		return BASE_URL+CITY_HOME_URL;
	}
	public static String POLL_SERVICE() {
		return BASE_URL+POLL_SERVICE_URL;
	}
}
