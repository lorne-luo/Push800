package push800.photograph.launcher;

import com.mobclick.android.MobclickAgent;

import push800.photograph.main.MainUI_Single;
import android.R.string;
import android.app.Activity;
import android.app.AlertDialog;
import android.app.ListActivity;
import android.os.Bundle;
import android.os.Handler;
import android.preference.PreferenceManager;
import android.util.Log;
import android.view.KeyEvent;
import android.view.View;
import android.view.Window;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.ArrayAdapter;
import android.widget.FrameLayout;
import android.widget.ListView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.AdapterView.OnItemSelectedListener;
import android.content.DialogInterface;
import android.content.Intent;
import push800.photograph.R;
import android.widget.RadioButton;
import push800.photograph.utils.City;
import push800.photograph.utils.DialogFactory;
import push800.photograph.utils.PreferencesUtil;
import push800.photograph.utils.StaticMethod;

public class SelectCityUI extends ListActivity {

	private static final String TAG = "SelectCityUI";
	private ListView cityList = null;

	@Override
	protected void onCreate(Bundle paramBundle) {
		super.onCreate(paramBundle);
		//友盟统计，错误报告
		MobclickAgent.onError(this);
		
		setContentView(R.layout.select_city);
		ListView lv = getListView();

		String[] cityList = getResources().getStringArray(R.array.city_list);
		ArrayAdapter<String> aa = new ArrayAdapter<String>(this,
				R.layout.select_city_item, cityList);
		setListAdapter(aa);
		Log.v(TAG, "Select City ListView Loaded");

		lv.setOnItemClickListener(new OnItemClickListener() {
			@Override
			public void onItemClick(AdapterView<?> parent, View view,
					int position, long id) {
				String cityName = (String) ((TextView) view).getText();
				int cityID = City.getIDByName(cityName);

				// Toast.makeText(SelectCityUI.this,
				// StaticMethod.getPhone(SelectCityUI.this),
				// Toast.LENGTH_LONG).show();

				// 把用户选择的城市id到preference中，下次WelcomeUI启动后跳过此UI直接进入相应城市
				PreferencesUtil.putInt("USER_CITY_ID", cityID,
						SelectCityUI.this);
				Log.v(TAG, "ListView item clicked " + cityName + "=" + cityID);

				// 转到main窗口
				Intent intent = new Intent().setClass(SelectCityUI.this,
						MainUI_Single.class);
				intent.putExtra("cityID", cityID);
				setResult(RESULT_OK, intent);
				finish();
			}
		});
	}

	@Override
	// 设置回退
	public boolean onKeyDown(int keyCode, KeyEvent event) {
		if (keyCode == KeyEvent.KEYCODE_BACK) {
			// Log.v(TAG, "KEYCODE_BACK");

			Log.v(TAG, "KEYCODE_BACK=2");
			AlertDialog ad = DialogFactory.getConfirmAlert(this, "确认退出",
					"真的要退出应用？", new DialogInterface.OnClickListener() {
						@Override
						public void onClick(DialogInterface dialog, int which) {
							Log.v(TAG, "KEYCODE_BACK quit");
							finish();
							System.exit(0);
						}
					});
			ad.show();

			return true;
		} else {
			// 非KEYCODE_BACK
			return super.onKeyDown(keyCode, event);
		}
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
}
