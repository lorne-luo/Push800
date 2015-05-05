package push800.photograph.launcher;

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
 * 此UI无实质功能，显示启动欢迎界面
 */
public class WelcomeUI extends Activity {
	private static final String TAG="WelcomeUI";
	
	@Override
	protected void onCreate(Bundle paramBundle) {
		requestWindowFeature(Window.FEATURE_NO_TITLE);
		super.onCreate(paramBundle);
		setContentView(R.layout.welcome);
//		int[] ids=new int[]{R.drawable.welcome1,R.drawable.welcome2,R.drawable.welcome3,R.drawable.welcome4,R.drawable.welcome5};
//		Random random=new Random();
//		int i=random.nextInt(5);
		ImageView bgiv = (ImageView) findViewById(R.id.welcome_iv);
//		bgiv.setBackgroundResource(ids[i]);
		bgiv.setBackgroundResource(R.drawable.welcome1);
		
		Handler handler = new Handler();
		WelcomeDelayer delayer = new WelcomeDelayer(this);
		handler.postDelayed(delayer, 1700);
	}
 
	@Override
	public boolean onKeyDown(int keyCode, KeyEvent event) {
		if (keyCode==KeyEvent.FLAG_KEEP_TOUCH_MODE) {
			
		}
		return true;
	}

	final class WelcomeDelayer implements Runnable {
		private WelcomeUI launcherUI = null;

		public WelcomeDelayer(WelcomeUI paramUI) {
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
