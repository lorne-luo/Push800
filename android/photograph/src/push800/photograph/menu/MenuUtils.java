package push800.photograph.menu;

import java.util.ArrayList;
import java.util.List;
import push800.photograph.menu.MenuInfo;
import push800.photograph.R;


/**
 * 所有menu按钮出现的按钮都设置在这里 
 * @author Leo
 */
public class MenuUtils {
	//所有菜单类型在这里编号
	public static final int MENU_SETTING=1;
	public static final int MENU_LOGOUT=2;
	public static final int MENU_ABOUT=3;
	public static final int MENU_EXIT=4;
	public static final int MENU_LOGIN=5;
	public static final int MENU_EXCHCITY=6;
	public static final int MENU_SUBSCRIBE=7;
	
	//浏览器操作
	public static final int MENU_REFRESH=8;
	public static final int MENU_GOFORWARD=9;
	public static final int MENU_GOBACK=10;
	
	
	//
	private static List<MenuInfo> initMenu(){
		List<MenuInfo> list=new ArrayList<MenuInfo>();
		//list.add(new MenuInfo(MENU_LOGIN,"用户登录",R.drawable.menu_ic_user,false));
		//list.add(new MenuInfo(MENU_SETTING,"更改设置",R.drawable.menu_ic_setting,false));
		list.add(new MenuInfo(MENU_ABOUT,"关于我们",R.drawable.menu_ic_help,false));
		list.add(new MenuInfo(MENU_EXIT,"退出应用",R.drawable.menu_ic_exit,false));
		return list;
	}
	
	/**
	 * 获取当前菜单列表
	 * @return
	 */
	public static List<MenuInfo> getBrowserList(){
		List<MenuInfo> list=initMenu();
		//list.add(0,new MenuInfo(MENU_GOFORWARD,"前进",R.drawable.menu_ic_goforward,false));
		//list.add(0,new MenuInfo(MENU_GOBACK,"后退",R.drawable.menu_ic_goback,false));
		list.add(0,new MenuInfo(MENU_REFRESH,"刷新页面",R.drawable.menu_ic_refresh,false));
		list.add(0,new MenuInfo(MENU_EXCHCITY,"切换城市",R.drawable.menu_ic_exchange,false));
		return list;
	}

	public static List<MenuInfo> getUserCenterList() {
		List<MenuInfo> list=initMenu();
		return list;
	}

	public static List<MenuInfo> getSettingList() {
		List<MenuInfo> list=initMenu();
		return list;
	}
}
