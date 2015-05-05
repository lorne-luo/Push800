package push800.photograph.launcher;

import push800.photograph.login.LoginActivity;
import push800.photograph.subscribe.UserCenterActivity;
import android.R.integer;
import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentActivity;
import android.support.v4.app.FragmentManager;
import android.support.v4.view.ViewPager;
import android.util.Log;
import android.view.KeyEvent;
import android.view.MenuItem;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.Window;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;
import android.content.Intent;
import push800.photograph.R;
import java.util.Random;

import com.viewpagerindicator.PageIndicator;
import com.viewpagerindicator.TabPageIndicator;
import com.viewpagerindicator.TitleProvider;

/*
 * 测试界面的，无用，关联tab_demo和toolbar两个layout
 */
public class TestUI2 extends FragmentActivity {
	private static final String TAG = "WelcomeUI";
	private static final String[] CONTENT = new String[] { "Recent", "Artists",
			"Albums", "Songs", "Playlists", "Genres" };
	private static final Random RANDOM = new Random();

	TestFragmentAdapter mAdapter;
	ViewPager mPager;
	PageIndicator mIndicator;

	private TextView currentMenu;
	TextView btn_home;
	TextView btn_usercenter;
	TextView btn_setting;
	TextView btn_settings;

	@Override
	protected void onCreate(Bundle paramBundle) {
		requestWindowFeature(Window.FEATURE_NO_TITLE);
		super.onCreate(paramBundle);
		setContentView(R.layout.deal_main);

		mAdapter = new GoogleMusicAdapter(getSupportFragmentManager());
		mPager = (ViewPager) findViewById(R.id.viewpager);
		mPager.setAdapter(mAdapter);

		mIndicator = (TabPageIndicator) findViewById(R.id.indicator);
		mIndicator.setViewPager(mPager);

		btn_home = (TextView) findViewById(R.id.menu_menu);
		btn_usercenter = (TextView) findViewById(R.id.menu_search);
//		btn_settings = (TextView) findViewById(R.id.menu_settings);
//		btn_setting = (TextView) findViewById(R.id.menu_setting);
		currentMenu = btn_home;
		setButtonOnClickListener();
	}

	protected void setButtonOnClickListener() {
		btn_home.setOnClickListener(new Home_OnClickListener());
		btn_usercenter.setOnClickListener(new UserCenter_OnClickListener());
		btn_settings.setOnClickListener(new Setting_OnClickListener());
		btn_setting.setOnClickListener(new Setting_OnClickListener());
	}

	//底部菜单，点击home
	class Home_OnClickListener implements View.OnClickListener {
		@Override
		public void onClick(View v) {
			Toast.makeText(TestUI2.this, "Home", Toast.LENGTH_SHORT).show();
			currentMenu.setBackgroundResource(0);
			currentMenu=(TextView)v;
			v.setBackgroundResource(R.drawable.bg_menu_selected);
		}
	}

	//底部菜单，点击usercenter
	class UserCenter_OnClickListener implements OnClickListener {
		@Override
		public void onClick(View v) {
			Toast.makeText(TestUI2.this, "UserCenter", Toast.LENGTH_SHORT)
					.show();
			currentMenu.setBackgroundResource(0);
			currentMenu=(TextView)v;
			v.setBackgroundResource(R.drawable.bg_menu_selected);
		}
	}

	//底部菜单，点击settings
	class Setting_OnClickListener implements OnClickListener {
		@Override
		public void onClick(View v) {
			Toast.makeText(TestUI2.this, "Setting", Toast.LENGTH_SHORT).show();
			currentMenu.setBackgroundResource(0);
			currentMenu=(TextView)v;
			v.setBackgroundResource(R.drawable.bg_menu_selected);
		}
	}

	class GoogleMusicAdapter extends TestFragmentAdapter implements
			TitleProvider {
		public GoogleMusicAdapter(FragmentManager fm) {
			super(fm);
		}

		@Override
		public Fragment getItem(int position) {
			return TestFragment.newInstance(TestUI2.CONTENT[position
					% TestUI2.CONTENT.length]);
		}

		@Override
		public int getCount() {
			return TestUI2.CONTENT.length;
		}

		@Override
		public String getTitle(int position) {
			return TestUI2.CONTENT[position % TestUI2.CONTENT.length]
					.toUpperCase();
		}
	}
}
