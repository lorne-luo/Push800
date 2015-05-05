package push800.photograph.launcher;

import net.youmi.android.AdManager;
import push800.photograph.main.MainUI_Single;
import push800.photograph.subscribe.UserCenterActivity;
import push800.photograph.utils.City;
import push800.photograph.utils.PreferencesUtil;
import push800.photograph.utils.Urls;
import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.preference.PreferenceManager;
import android.util.Log;
import android.view.KeyEvent;
import android.view.Window;
import android.widget.Toast;
import android.content.Intent;
import push800.photograph.R;

import com.feedback.NotificationType;
import com.feedback.UMFeedbackService;
import com.mobclick.android.MobclickAgent;
import com.mobclick.android.ReportPolicy;
/*
 * APP启动的第一个activity
 * 先调用welcomeUI,结束后 若用户曾经选择过城市则直接进入相应城市的MainUI
 * 否则进入SelectCityUI
 */
public class LauncherUI extends Activity {

	private static final String TAG = "LauncherUI";

	@Override
	protected void onCreate(Bundle paramBundle) {
		requestWindowFeature(Window.FEATURE_NO_TITLE);
		super.onCreate(paramBundle);
		//      应用Id          应用密码        广告请求间隔(s)   设置测试模式[false为发布模式] 
		AdManager.init(this,"620d23a9e60a9e18", "620d23a9e60a9e18", 30, false);
		//友盟统计，3天检查一次更新
		MobclickAgent.update(this,1000*60*60*24*3);
		MobclickAgent.updateOnlineConfig(this);
		UMFeedbackService.enableNewReplyNotification(this, NotificationType.AlertDialog);
		
		Log.v(this.toString(), "LauncherUI onCreate");
	}

	@Override
	protected void onResume() {
		super.onResume();
		Log.v(this.toString(), "LauncherUI onResume");
		Intent intent = new Intent(this, WelcomeUI.class);
		startActivityForResult(intent, 99);
	}

	@Override
	protected void onActivityResult(int requestCode, int resultCode, Intent data) {
		super.onActivityResult(requestCode, resultCode, data);
		Log.v(TAG, "requestCode=" + String.valueOf(requestCode));
		
		overridePendingTransition(android.R.anim.slide_in_left,
				android.R.anim.slide_out_right);
		
		if (resultCode == RESULT_OK) {
			if (requestCode==99) {//从欢迎界面返回
				int cityID = PreferencesUtil.getInt("USER_CITY_ID", 0,
						LauncherUI.this);
				Log.v(TAG, "cityID=" + String.valueOf(cityID));

				if (cityID < 1) {//没有城市信息
					Intent intent2 = new Intent()
							.setClass(this, SelectCityUI.class);
					startActivityForResult(intent2,2);
				} else {//有
					Intent intent2 = new Intent().setClass(this,
							MainUI_Single.class);
					intent2.putExtra("cityID", cityID);
					startActivity(intent2);
					finish();
				}
			}else if (requestCode==2) {
				Bundle b = data.getExtras(); 
				int cid = b.getInt("cityID",1);
				Intent intent2 = new Intent().setClass(this,
						MainUI_Single.class);
				intent2.putExtra("cityID", cid);
				startActivity(intent2);
				finish();
			}
		}else if (resultCode == RESULT_CANCELED) {
			if (requestCode==2) {
				System.exit(0);
				finish();
			}
		}
	}
	
	
}
