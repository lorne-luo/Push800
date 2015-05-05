package push800.photograph.launcher;

import push800.photograph.login.LoginActivity;
import push800.photograph.subscribe.UserCenterActivity;
import android.R.integer;
import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.KeyEvent;
import android.view.Window;
import android.widget.ImageView;
import android.content.Intent;
import push800.photograph.R;
import java.util.Random;

/*
 * 测试界面的，无用，关联tab_demo和toolbar两个layout
 */
public class TestUI extends Activity {
	private static final String TAG="WelcomeUI";
	
	@Override
	protected void onCreate(Bundle paramBundle) {
		requestWindowFeature(Window.FEATURE_NO_TITLE);
		super.onCreate(paramBundle);
		setContentView(R.layout.tab_demo);
		
		Handler handler = new Handler();
		WelcomeDelayer delayer = new WelcomeDelayer(this);
		handler.postDelayed(delayer, 1700);
	}
	
	
	
	final class WelcomeDelayer implements Runnable {
		private TestUI launcherUI = null;

		public WelcomeDelayer(TestUI paramUI) {
			this.launcherUI = paramUI;
		}

		public final void run() {
			Intent intent = new Intent();
			// intent.setClass(this.launcherUI,LoginActivity.class);
			// startActivity(intent);
			this.launcherUI.setResult(RESULT_OK, intent);
			this.launcherUI.finish();
		}
	}
}
