package push800.photograph.main;

import java.io.File;
import java.io.UnsupportedEncodingException;
import java.lang.reflect.Method;
import java.util.List;

import com.feedback.UMFeedbackService;
import com.mobclick.android.MobclickAgent;
import org.apache.http.util.EncodingUtils;

import push800.photograph.R;
import push800.photograph.launcher.SelectCityUI;
import push800.photograph.menu.MenuAdapter;
import push800.photograph.menu.MenuInfo;
import push800.photograph.menu.MenuUtils;
import push800.photograph.subscribe.SearchActivity;
import push800.photograph.utils.City;
import push800.photograph.utils.DialogFactory;
import push800.photograph.utils.PreferencesUtil;
import push800.photograph.utils.Urls;
import push800.photograph.utils.StaticMethod;
import android.R.integer;
import android.app.Activity;
import android.app.AlertDialog;
import android.app.ProgressDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.GestureDetector;
import android.view.GestureDetector.OnGestureListener;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.Menu;
import android.view.MenuItem;
import android.view.MotionEvent;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.View.OnFocusChangeListener;
import android.view.View.OnTouchListener;
import android.view.ViewGroup.LayoutParams;
import android.view.Window;
import android.webkit.CacheManager;
import android.webkit.JsResult;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.Button;
import android.widget.GridView;
import android.widget.PopupWindow;
import android.widget.TextView;
import android.widget.Toast;

public class MainUI_Single extends Activity implements OnGestureListener,
		OnTouchListener {
	private static String TAG = "MainUI_Single";
	private WebView webView = null;
	// private ProgressDialog dialog;

	private int cityID = 0;// 当前选择的城市id，通常是由SelectCityUI传入
	private int nCurrentTab = 0;// tabhost控件当前显示的tab编号
	private int backPressTimes = 0;// 记录连续按back的次数，若连续按两次则退出程序

	Button currentMenu;
	Button btn_menu;
	Button btn_search;
	Button btn_goforward;
	Button btn_goback;

	// 为了在用户中心界面和设置界面能弹出菜单，这里几个变量都设为static
	// 定义popupwindow
	public static PopupWindow popup;
	// 定义适配器
	public static MenuAdapter menuAdapter;
	// 菜单项列表
	public static List<MenuInfo> menulists;
	// 定义gridview
	public static GridView menuGridView;

	// 浏览器手势
	private GestureDetector gestureDetector;
	private static final int SWIPE_MIN_DISTANCE = 120;
	private static final int SWIPE_THRESHOLD_VELOCITY = 200;

	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		// 友盟统计，错误报告
		MobclickAgent.onError(this);

		// 设置特性以允许在应用程序的标题栏上显示进度条（条状）
		requestWindowFeature(Window.FEATURE_PROGRESS);
		// 设置特性以允许在应用程序的标题栏上显示进度条（圆圈状）
		requestWindowFeature(Window.FEATURE_INDETERMINATE_PROGRESS);
		setContentView(R.layout.mainform_single);

		Intent intent = getIntent();
		this.cityID = intent.getIntExtra("cityID", 0);
		this.nCurrentTab = intent.getIntExtra("CurrentTab", 0);
		Log.v(TAG, "mainform_single cityid=" + String.valueOf(this.cityID));
		this.webView = (WebView) findViewById(R.id.webview);

		// 在标题栏上显示进度条（条状）
		setProgressBarVisibility(true);
		// 在标题栏上显示进度条（圆圈状）
		setProgressBarIndeterminateVisibility(true);

		setButtonOnClickListener();
		initPopuWindows();// 初始化menu菜单
		initWebView();// 初始化浏览器
	}

	// 初始浏览器
	private void initWebView() {
		WebSettings settings = webView.getSettings();
		settings.setJavaScriptEnabled(true);
		settings.setSupportMultipleWindows(false);
		settings.setJavaScriptCanOpenWindowsAutomatically(false);
		settings.setPluginsEnabled(true);
		settings.setSupportZoom(false);
		settings.setUserAgent(0);// 手机用户
		settings.setCacheMode(android.webkit.WebSettings.LOAD_CACHE_ELSE_NETWORK);
		settings.setUserAgentString("Mozilla/5.0 (Linux; U; Android; WAP; 240*300) UCWEB7.9");// 设置浏览器的useragent

		webView.setOnTouchListener(this);// 监听触摸事件
		webView.setClickable(true);
		webView.setLongClickable(true);
		webView.setScrollbarFadingEnabled(true);// 消去垂直滚动条的白色底色
		webView.setScrollBarStyle(View.SCROLLBARS_INSIDE_OVERLAY);

		webView.setWebViewClient(new MyClient());// 两个重要的控制webview的类
		webView.setWebChromeClient(new MyChromeClient());

		// 实现javascript和android的互相调用，这里主要是处理点击搜索按钮时
		webView.addJavascriptInterface(new JavaScriptInterface(), "javaobj");

		// webView.requestFocus();
		// url=首页+城市名
		webView.clearCache(true);
		webView.loadUrl(Urls.CITY_HOME() + City.getShortNameByID(this.cityID));
		if (this.cityID > 0) {
			String city = City.getNameByID(this.cityID);
			setTitle(city + "二手摄影器材");
			Toast.makeText(MainUI_Single.this.getApplicationContext(),
					"      前往" + city + "版面\n\n点击菜单可切换城市", Toast.LENGTH_SHORT)
					.show();
		}
		// webView.loadUrl( "file:///android_asset/XX.html" ); 

		gestureDetector = new GestureDetector(this);
	}

	protected void setButtonOnClickListener() {
		btn_menu = (Button) findViewById(R.id.menu_menu);
		btn_search = (Button) findViewById(R.id.menu_search);
		btn_goback = (Button) findViewById(R.id.go_back);
		btn_goforward = (Button) findViewById(R.id.go_forward);
		currentMenu = btn_menu;
		btn_menu.setOnClickListener(new Menu_OnClickListener());
		btn_search.setOnClickListener(new Search_OnClickListener());
		btn_goback.setOnClickListener(new GoBack_OnClickListener());
		btn_goforward.setOnClickListener(new GoForward_OnClickListener());
	}

	// 底部菜单-菜单
	class Menu_OnClickListener implements View.OnClickListener {
		@Override
		public void onClick(View v) {
			onMenuOpened(0, null);
		}
	}

	// 底部菜单-搜索
	class Search_OnClickListener implements OnClickListener {
		@Override
		public void onClick(View v) {
			Intent intent = new Intent().setClass(MainUI_Single.this,
					SearchActivity.class);
			intent.putExtra("cityID", cityID);
			startActivityForResult(intent, 2);
		}
	}

	// 底部菜单，点击前进
	class GoBack_OnClickListener implements OnClickListener {
		@Override
		public void onClick(View v) {
			if (webView.canGoBack()) {
				webView.goBack();
			}
		}
	}

	// 底部菜单，点击后退
	class GoForward_OnClickListener implements OnClickListener {
		@Override
		public void onClick(View v) {
			if (webView.canGoForward()) {
				webView.goForward();
			}
		}
	}

	// 自定义的WebViewClient
	private class MyClient extends WebViewClient {
		@Override
		// 这里只能捕捉到程序中loadurl的访问，用户的点击要用onPageStarted来截获
		public boolean shouldOverrideUrlLoading(WebView view, String url) {
			// 如果是push800://协议说明这是需要使用控件响应的命令
			if (url.startsWith("push800://")) {
				view.stopLoading();
				// MainUI.this.webView.stopLoading();

				String command = url.substring(10);
				Log.v(TAG, "inner command=" + command);
				Intent intent = new Intent();
				if (command.equals("login")) {
					// intent.setClass(MainUI_Single.this, LoginActivity.class);
				} else if (command.equals("register")) {
					// intent.setClass(MainUI_Single.this,
					// RegisterActivity.class);
				} else if (command.equals("subscribe")) {
					// intent.setClass(MainUI_Single.this,
					// RegisterActivity.class);
				} else if (command.equals("search")) {
					// intent.setClass(MainUI.this, SearchActivity.class);
					return false;
				} else {
					// 命令无法识别则不作响应
					return true;
				}
				startActivity(intent);
				return true;
			} else {
				return false;
			}
		}

		public void onProgressChanged(WebView view, int newProgress) {
			// activity的进度是0 to 10000 (both inclusive),所以要*100
			setProgress(newProgress * 100);
		}

		@Override
		// 页面开始加载
		public void onPageStarted(WebView view, String url, Bitmap favicon) {
			// dialog=ProgressDialog.show(MainUI.this, "", "Loading...", true);
			// super.onPageStarted(view, url, favicon);
			if (url.endsWith("pe/subscribe")) {
				Log.v(TAG, "url endwith = pe/subscribe");
			}
		}

		@Override
		public void onReceivedError(WebView view, int errorCode,
				String description, String failingUrl) {
			// TODO Auto-generated method stub
		}

		private void setEmbeddedTitleBar(WebView web, View titlebar) {
			try {
				Method m = WebView.class.getMethod("setEmbeddedTitleBar",
						new Class[] { View.class });
				m.invoke(web, titlebar);
			} catch (Exception e) {
				Log.d("TEST", "Err: " + e.toString());
			}
		}
	}

	// 自定义的WebChromeClient
	// WebChromeClient提供progress的操作
	private class MyChromeClient extends WebChromeClient {
		@Override
		public void onProgressChanged(WebView view, int newProgress) {
			// activity的进度是0 to 10000 (both inclusive),所以要*100
			setProgress(newProgress * 100);
		}

		@Override
		public void onReceivedTitle(WebView view, String title) {
			// 设置当前activity的标题栏
			setTitle(title);
			super.onReceivedTitle(view, title);
		}

		@Override
		// 替换webview默认的alert弹框方式
		public boolean onJsAlert(WebView view, String url, String message,
				final JsResult result) {
			new AlertDialog.Builder(MainUI_Single.this)
					.setTitle(message)
					.setPositiveButton("确定",
							new DialogInterface.OnClickListener() {
								@Override
								public void onClick(DialogInterface dialog,
										int which) {
									result.confirm();
								}
							}).show();
			return true;
		}
	}

	@Override
	// 设置回退
	public boolean onKeyDown(int keyCode, KeyEvent event) {
		if (keyCode == KeyEvent.KEYCODE_BACK) {
			// Log.v(TAG, "KEYCODE_BACK");
			if (this.nCurrentTab == 0 && webView.canGoBack()) {
				Log.v(TAG, "KEYCODE_BACK=1");
				webView.goBack();
				this.backPressTimes = 0;
				return true;
			} else {
				Log.v(TAG, "KEYCODE_BACK=2");
				AlertDialog ad = DialogFactory.getConfirmAlert(this, "确认退出",
						"真的要退出应用？", new DialogInterface.OnClickListener() {
							@Override
							public void onClick(DialogInterface dialog,
									int which) {
								Log.v(TAG, "MainUI finished");
								// MainUI_Single.this.finish();
								finish();
								System.exit(0);
							}
						});
				ad.show();

				return true;
			}
		} else {
			// 非KEYCODE_BACK
			return super.onKeyDown(keyCode, event);
		}
	}

	// 按MENU键
	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// menu.add(0, 1, 1, R.string.menu_selcity);
		// menu.add(0, 2, 2, R.string.menu_setting);
		// menu.add(0, 3, 3, R.string.menu_about);
		// menu.add(0, 4, 4, R.string.menu_exit);
		// return super.onCreateOptionsMenu(menu);
		menu.add("Cremenu");
		return super.onCreateOptionsMenu(menu);
	}

	// 点选MENU弹出的菜单项
	@Override
	public boolean onOptionsItemSelected(MenuItem item) {
		switch (item.getItemId()) {
		case 4: // 退出
			AlertDialog ad = DialogFactory.getConfirmAlert(this, "确认退出",
					"真的要退出应用？", new DialogInterface.OnClickListener() {
						@Override
						public void onClick(DialogInterface dialog, int which) {
							Log.v(TAG, "MainUI finished");
							MainUI_Single.this.finish();
							// System.exit(0);
						}
					});
			ad.show();
			break;
		case 1: // 切换城市

			break;
		case 2: // 设置

			break;
		case 3: // 关于
			showAbout();
			break;
		}

		return super.onOptionsItemSelected(item);
	}

	public void showAbout() { // 显示关于信息
		String aboutInfo = MobclickAgent.getConfigParams(this, "about");
		if (aboutInfo.equals("")) {
			aboutInfo = getString(R.string.about_tips);
		}

		new AlertDialog.Builder(MainUI_Single.this)
				.setTitle(R.string.title_about)
				.setMessage(aboutInfo)
				.setPositiveButton("反馈", new DialogInterface.OnClickListener() {
					public void onClick(DialogInterface dialoginterface, int i) {
						// Do Nothing
						UMFeedbackService
								.openUmengFeedbackSDK(MainUI_Single.this);
					}
				})
				.setNegativeButton(R.string.app_ISee,
						new DialogInterface.OnClickListener() {
							public void onClick(
									DialogInterface dialoginterface, int i) {
								// Do Nothing
							}
						}).show();
		return;
	}

	protected void Quit() {
		this.backPressTimes++;
		if (this.backPressTimes == 1) {
			Toast toast = Toast.makeText(this, "再次点击将退出", Toast.LENGTH_LONG);
			toast.show();
		}
		if (this.backPressTimes > 1) {
			this.backPressTimes = 0;
			System.exit(0);
			finish();
		}
	}

	/**
	 * 设置PopupWindows
	 */
	private void initPopuWindows() {
		// 初始化gridview
		menuGridView = (GridView) View.inflate(this, R.layout.gridview_menu,
				null);
		// 初始化PopupWindow,LayoutParams.WRAP_CONTENT,
		// LayoutParams.WRAP_CONTENT控制显示
		popup = new PopupWindow(menuGridView, LayoutParams.FILL_PARENT,
				LayoutParams.WRAP_CONTENT);
		// 设置menu菜单背景
		popup.setBackgroundDrawable(getResources().getDrawable(
				R.drawable.menu_background));
		// menu菜单获得焦点 如果没有获得焦点menu菜单中的控件事件无法响应
		popup.setFocusable(true);
		// 设置显示和隐藏的动画
		popup.setAnimationStyle(R.style.menushow);
		popup.update();
		// 设置触摸获取焦点
		menuGridView.setFocusableInTouchMode(true);
		// 设置键盘事件,如果按下菜单键则隐藏菜单
		menuGridView.setOnKeyListener(new android.view.View.OnKeyListener() {
			public boolean onKey(View v, int keyCode, KeyEvent event) {
				if ((keyCode == KeyEvent.KEYCODE_MENU) && (popup.isShowing())) {
					popup.dismiss();
					return true;
				}
				return false;
			}
		});
		// 添加菜单按钮事件
		menuGridView.setOnItemClickListener(new OnItemClickListener() {
			public void onItemClick(AdapterView<?> arg0, View arg1, int arg2,
					long arg3) {
				MenuInfo mInfo = menulists.get(arg2);
				popup.dismiss();
				if (mInfo.ishide) {
					return;
				}
				switch (mInfo.menuId) {
				case MenuUtils.MENU_EXIT:
					AlertDialog ad = DialogFactory.getConfirmAlert(
							MainUI_Single.this, "确认退出", "真的要退出应用？",
							new DialogInterface.OnClickListener() {
								@Override
								public void onClick(DialogInterface dialog,
										int which) {
									Log.v(TAG, "MainUI finished");
									MainUI_Single.this.finish();
									// System.exit(0);
								}
							});
					ad.show();
					break;
				case MenuUtils.MENU_EXCHCITY:
					// Toast.makeText(MainUI_Single.this, "切换城市", 0).show();
					Intent intent = new Intent().setClass(MainUI_Single.this,
							SelectCityUI.class);
					startActivityForResult(intent, 1);
					break;
				case MenuUtils.MENU_SETTING:
					// Toast.makeText(MainUI_Single.this, "设置", 0).show();
					break;
				case MenuUtils.MENU_ABOUT:
					// Toast.makeText(MainUI_Single.this, "关于我们", 0).show();
					showAbout();
					break;
				case MenuUtils.MENU_REFRESH:
					Toast.makeText(MainUI_Single.this, "刷新页面", 0).show();
					webView.clearCache(true);
					// WebSettings settings = webView.getSettings();
					// settings.setCacheMode(android.webkit.WebSettings.LOAD_NO_CACHE);
					webView.reload();
					// settings.setCacheMode(android.webkit.WebSettings.LOAD_CACHE_ELSE_NETWORK);
					break;
				case MenuUtils.MENU_GOBACK:
					if (webView.canGoBack()) {
						webView.goBack();
						Toast.makeText(MainUI_Single.this, "页面后退", 0).show();
					}
					break;
				case MenuUtils.MENU_GOFORWARD:
					if (webView.canGoForward()) {
						webView.goForward();
						Toast.makeText(MainUI_Single.this, "页面前进", 0).show();
					}
					break;
				case MenuUtils.MENU_LOGIN:
					// Toast.makeText(MainUI_Single.this, "用户登录", 0).show();

					break;
				}
			}
		});
	}

	@Override
	protected void onActivityResult(int requestCode, int resultCode, Intent data) {
		Log.v(TAG, "requestCode=" + String.valueOf(requestCode)
				+ " resultCode=" + String.valueOf(resultCode));
		switch (resultCode) { // resultCode为回传的标记，我在B中回传的是RESULT_OK
		case RESULT_OK:
			if (requestCode == 1) {// 切换城市
				Bundle b = data.getExtras();
				int cid = b.getInt("cityID", this.cityID);
				if (cid != this.cityID) {
					this.cityID = cid;
					webView.clearCache(true);
					webView.loadUrl(Urls.CITY_HOME()
							+ City.getShortNameByID(this.cityID));
				}
			} else if (requestCode == 2) {// 搜索
				// ?city_id=1&brand_id=1&keyword=ssdd&min_price=600&max_price=800
				// &quality=98
				Bundle b = data.getExtras();
				int cid = b.getInt("cityID", this.cityID);
				int bid = b.getInt("brandID", 0);
				int minp = b.getInt("minPrice", 0);
				int maxp = b.getInt("maxPrice", 0);
				int quality = b.getInt("quality", 0);
				String keyword = b.getString("keyword");

				String url = Urls.CITY_HOME() + City.getShortNameByID(cid)
						+ "/?brand_id=" + String.valueOf(bid) + "&keyword="
						+ keyword + "&quality=" + String.valueOf(quality)
						+ "&min_price=" + String.valueOf(minp) + "&max_price="
						+ String.valueOf(maxp);
				Log.v(TAG, "searchurl=" + url);

				webView.loadUrl(url);

				this.cityID = cid;
				PreferencesUtil.putInt("USER_CITY_ID", cityID,
						MainUI_Single.this);
				PreferencesUtil.putInt("SEARCH_BRAND_ID", bid,
						MainUI_Single.this);
				PreferencesUtil.putInt("SEARCH_QUALITY", quality,
						MainUI_Single.this);
				PreferencesUtil.putInt("SEARCH_MIN_PRICE", minp,
						MainUI_Single.this);
				PreferencesUtil.putInt("SEARCH_MAX_PRICE", maxp,
						MainUI_Single.this);
				PreferencesUtil.putString("SEARCH_KEYWORD", keyword,
						MainUI_Single.this);

			}

			break;
		default:
			break;
		}

	}

	@Override
	public boolean onMenuOpened(int featureId, Menu menu) {
		Log.v(TAG, "onMenuOpened-" + String.valueOf(nCurrentTab));
		if (popup != null) {
			switch (this.nCurrentTab) {
			case 0:// 浏览器界面
				menulists = MenuUtils.getBrowserList();
				break;
			case 1:// 用户中心界面
				menulists = MenuUtils.getUserCenterList();
				break;
			case 2:// 设置界面
				menulists = MenuUtils.getSettingList();
				break;
			default:
				break;
			}
			menuAdapter = new MenuAdapter(this, menulists);
			menuGridView.setAdapter(menuAdapter);
			popup.showAtLocation(this.findViewById(R.id.linearlayout),
					Gravity.BOTTOM, 0, 55);
		}
		return false;// 返回为true 则显示系统menu
	}

	@Override
	public boolean onPrepareOptionsMenu(Menu menu) {
		menu.add("Premenu");
		return super.onPrepareOptionsMenu(menu);
	}

	final class JavaScriptInterface {
		JavaScriptInterface() {
		}

		// // 页面点击search按钮
		// public void searchClick(int id, String keyword) {//
		// 注意这里的名称。它为clickOnAndroid(),注意，注意，严重注意
		// Toast toast = Toast.makeText(MainUI.this, "clickOnAndroid",
		// Toast.LENGTH_LONG);
		// // 先将搜索信息存入preference
		// PreferencesUtil.putInt("SEARCH_BRAND_ID", id, MainUI.this);
		// PreferencesUtil.putString("SEARCH_KEYWORD", keyword, MainUI.this);
		// Log.v(TAG, "searchClick " + String.valueOf(id) + " = " + keyword
		// + " cityid=" + String.valueOf(MainUI.this.cityID));
		//
		// // 然后跳转到相应的搜索结果页面
		// try {
		// String searchUrl = Urls.CITY_HOME()
		// + City.getShortNameByID(MainUI.this.cityID) + "?brand_id="
		// + String.valueOf(id) + "&keyword=" +
		// java.net.URLEncoder.encode(keyword,"utf-8");
		// //webView.loadUrl(searchUrl);
		// Log.v(TAG, "searchUrl = " +
		// java.net.URLEncoder.encode(keyword,"utf-8"));
		// } catch (UnsupportedEncodingException e) {
		// // TODO Auto-generated catch block
		// e.printStackTrace();
		// }
		// }
		//
		// public void subscribe_submit(){
		// String phone_ime=StaticMethod.getPhoneIME(MainUI.this);
		// String phone_number=StaticMethod.getPhoneNumber(MainUI.this);
		// webView.loadUrl("javascript:subscribe_submit('"+phone_number+"','"+phone_ime+"')");
		// }

		// 设置手机号码和ime
		public void setPhoneNumber() {
			if (false) {
				String phone_ime = StaticMethod.getPhoneIME(MainUI_Single.this);
				String phone_number = StaticMethod
						.getPhoneNumber(MainUI_Single.this);
				webView.loadUrl("javascript:setPhoneNumber('" + phone_number
						+ "','" + phone_ime + "')");
			}
		}

		public void alert(String title, String msg) {
			AlertDialog ad = DialogFactory.getAlert(MainUI_Single.this,
					"title", msg);
			ad.show();
		}
	}

	@Override
	public void onDestroy() {
		File file = CacheManager.getCacheFileBaseDir();
		if (file != null && file.exists() && file.isDirectory()) {
			for (File item : file.listFiles()) {
				item.delete();
			}
			file.delete();
		}
		this.deleteDatabase("webview.db");
		this.deleteDatabase("webviewCache.db");
		super.onDestroy();
	}

	@Override
	public void onResume() {
		super.onResume();
		MobclickAgent.onResume(this);
	}

	@Override
	public void onPause() {
		super.onResume();
		MobclickAgent.onPause(this);
	}

	// gestureDetector method
	@Override
	public boolean onDown(MotionEvent arg0) {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public boolean onFling(MotionEvent e1, MotionEvent e2, float VelocityX,
			float VelocityY) {
		// TODO Auto-generated method stub
		if (e1.getX() - e2.getX() > SWIPE_MIN_DISTANCE
				&& Math.abs(VelocityX) > SWIPE_THRESHOLD_VELOCITY) {
			if (webView.canGoForward()) {
				webView.goForward();
				Toast.makeText(this, "页面前进", Toast.LENGTH_SHORT).show();
			}
		} else if (e2.getX() - e1.getX() > SWIPE_MIN_DISTANCE
				&& Math.abs(VelocityX) > SWIPE_THRESHOLD_VELOCITY) {
			if (webView.canGoBack()) {
				webView.goBack();
				Toast.makeText(this, "页面后退", Toast.LENGTH_SHORT).show();
			}
		}
		return false;
	}

	@Override
	public void onLongPress(MotionEvent arg0) {
		// TODO Auto-generated method stub

	}

	@Override
	public boolean onScroll(MotionEvent arg0, MotionEvent arg1, float arg2,
			float arg3) {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public void onShowPress(MotionEvent arg0) {
		// TODO Auto-generated method stub

	}

	@Override
	public boolean onSingleTapUp(MotionEvent arg0) {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public boolean onTouch(View arg0, MotionEvent arg1) {
		// TODO Auto-generated method stub
		return gestureDetector.onTouchEvent(arg1);
	}
}
