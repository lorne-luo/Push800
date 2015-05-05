package push800.photograph.subscribe;

import java.util.ArrayList;
import java.util.List;

import org.apache.http.NameValuePair;
import org.apache.http.message.BasicNameValuePair;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import com.mobclick.android.MobclickAgent;

import push800.photograph.R;
import push800.photograph.R.string;
import push800.photograph.launcher.SelectCityUI;
import push800.photograph.main.MainUI_Single;
import push800.photograph.menu.MenuAdapter;
import push800.photograph.menu.MenuInfo;
import push800.photograph.menu.MenuUtils;
import push800.photograph.utils.City;
import push800.photograph.utils.PreferencesUtil;
import push800.photograph.utils.Urls;
import push800.photograph.utils.HttpUtil;
import android.R.integer;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.Display;
import android.view.Gravity;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.WindowManager;
import android.view.WindowManager.LayoutParams;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.Toast;
import android.widget.AdapterView.OnItemSelectedListener;

public class SearchActivity extends Activity {
	private static String TAG = "SubmitActivity";

	// 定义控件变量
	private Spinner spinner_city = null;
	private Spinner spinner_district = null;
	private Spinner spinner_brand = null;
	// private Spinner spinner_price = null;
	private Button submit_btn = null;
	private Button close_btn = null;
	private EditText min_price_et = null;
	private EditText max_price_et = null;
	private EditText keyword_et = null;
	private EditText quality_et = null;

	private int city_id = 0;

	// 定义变量
	private int nSelectedCity = 0;
	private int nSelectedDistrict = 0;
	private int nSelectedBrand = 0;
	// private int nSelectedPrice = 0;
	ArrayAdapter<CharSequence> adapter_district = null;

	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		//友盟统计，错误报告
		MobclickAgent.onError(this);
		
		setContentView(R.layout.message_search);

		WindowManager m = getWindowManager();
		Display d = m.getDefaultDisplay(); // 为获取屏幕宽、高
		LayoutParams p = getWindow().getAttributes(); // 获取对话框当前的参数值
		// p.height = (int) (d.getHeight() * 1.0); // 高度设置为屏幕的1.0
		p.width = (int) (d.getWidth() * 1.0); // 宽度设置为屏幕的0.8
		p.alpha = 1.0f; // 设置本身透明度
		p.dimAmount = 0.0f; // 设置黑暗度
		getWindow().setAttributes(p); // 设置生效
		getWindow().setGravity(Gravity.CENTER);

		Intent intent = getIntent();
		this.city_id = intent.getIntExtra("cityID", 0);

		// 得到控件对象
		spinner_city = (Spinner) findViewById(R.id.sp_city);

		// spinner_district = (Spinner) findViewById(R.id.sp_district);
		spinner_brand = (Spinner) findViewById(R.id.sp_brand);
		submit_btn = (Button) findViewById(R.id.submit_btn);
		close_btn = (Button) findViewById(R.id.close_btn);
		min_price_et = (EditText) findViewById(R.id.min_price_et);
		max_price_et = (EditText) findViewById(R.id.max_price_et);
		keyword_et = (EditText) findViewById(R.id.keyword_et);
		quality_et = (EditText) findViewById(R.id.quality_et);
		// spinner_price = (Spinner)findViewById(R.id.sp_price);

		// 为"城市"创建Adapter
		ArrayAdapter<CharSequence> adapter_city = ArrayAdapter
				.createFromResource(this, R.array.city_list,
						android.R.layout.simple_spinner_item);
		spinner_city.setAdapter(adapter_city);
		spinner_city.setPrompt("请选择城市");
		spinner_city.setOnItemSelectedListener(new SpinnerCityListener());
		spinner_city.setSelection(city_id-1);

		// 为"品牌"创建Adapter
		ArrayAdapter<CharSequence> adapter_brand = ArrayAdapter
				.createFromResource(this, R.array.brand_list,
						android.R.layout.simple_spinner_item);
		spinner_brand.setAdapter(adapter_brand);
		spinner_brand.setPrompt("请选择品牌");
		spinner_brand.setOnItemSelectedListener(new SpinnerBrandListener());

		// 在未选择城市之前，城区的spinner显示出城区两个字
		String[] district = new String[] { "城区" };
		ArrayAdapter<String> adapter = new ArrayAdapter<String>(this,
				android.R.layout.simple_spinner_item, district);
		// spinner_district.setPrompt("请先选择城市");
		// spinner_district.setAdapter(adapter);

		// 为"价格"创建Adapter
		// ArrayAdapter<CharSequence> adapter_price =
		// ArrayAdapter.createFromResource(
		// this,
		// R.array.price_list,
		// android.R.layout.simple_spinner_item);
		// spinner_price.setAdapter(adapter_price);
		// spinner_price.setPrompt("请选择品牌");
		// spinner_price.setOnItemSelectedListener(new SpinnerPriceListener());
		// spinner_price.setSelection(0);
		submit_btn.setOnClickListener(new SubmitButtionClickListener());
		close_btn.setOnClickListener(new CloseButtionClickListener());

		spinner_brand.setSelection(PreferencesUtil.getInt("SEARCH_BRAND_ID", 0,
				SearchActivity.this));
		quality_et.setText(String.valueOf(PreferencesUtil.getInt(
				"SEARCH_QUALITY", 0, SearchActivity.this)));
		min_price_et.setText(String.valueOf(PreferencesUtil.getInt(
				"SEARCH_MIN_PRICE", 0, SearchActivity.this)));
		max_price_et.setText(String.valueOf(PreferencesUtil.getInt(
				"SEARCH_MAX_PRICE", 0, SearchActivity.this)));
		keyword_et.setText(String.valueOf(PreferencesUtil.getString(
				"SEARCH_KEYWORD", "", SearchActivity.this)));
	}

	@Override
	// 弹出菜单的逻辑
	public boolean onMenuOpened(int featureId, Menu menu) {
		return false;
	}

	class SpinnerCityListener implements OnItemSelectedListener {

		@Override
		public void onItemSelected(AdapterView<?> arg0, View arg1, int arg2,
				long arg3) {
			long selected_id = arg0.getItemIdAtPosition(arg2);
			nSelectedCity = (int) selected_id;
			// String selected_str = arg0.getItemAtPosition(arg2).toString();
			// System.out.println(selected_id + " " + selected_str);
			int ID_DISTRICT_LIST = -1;

			switch (nSelectedCity) {
			case 0:
				// if (adapter_district != null)
				// spinner_district.setSelection(0);
				// spinner_district.setEnabled(false);
				return;
			case 1:
				ID_DISTRICT_LIST = R.array.bj_list;
				break;
			case 2:
				ID_DISTRICT_LIST = R.array.sh_list;
				break;
			case 3:
				ID_DISTRICT_LIST = R.array.gz_list;
				break;
			case 4:
				ID_DISTRICT_LIST = R.array.sz_list;
				break;
			case 5:
				ID_DISTRICT_LIST = R.array.tj_list;
				break;
			}
			// spinner_district.setEnabled(true);

			// 为"城区"创建Adapter
			// if(adapter_district != null)
			// adapter_district.clear();

			// adapter_district = ArrayAdapter.createFromResource(
			// SearchActivity.this, ID_DISTRICT_LIST,
			// android.R.layout.simple_spinner_item);
			// spinner_district.setAdapter(adapter_district);
			// spinner_district.setPrompt("请选择城区");
			// spinner_district
			// .setOnItemSelectedListener(new SpinnerDistrictListener());
			// spinner_district.setSelection(0);
		}

		@Override
		public void onNothingSelected(AdapterView<?> arg0) {
			// TODO Auto-generated method stub

		}
	}

	class SpinnerDistrictListener implements OnItemSelectedListener {

		@Override
		public void onItemSelected(AdapterView<?> arg0, View arg1, int arg2,
				long arg3) {
			long selected_id = arg0.getItemIdAtPosition(arg2);
			nSelectedDistrict = (int) selected_id;
			// String selected_str = arg0.getItemAtPosition(arg2).toString();
			// System.out.println(selected_id + " " + selected_str);
		}

		@Override
		public void onNothingSelected(AdapterView<?> arg0) {
			// TODO Auto-generated method stub

		}
	}

	class SpinnerBrandListener implements OnItemSelectedListener {

		@Override
		public void onItemSelected(AdapterView<?> arg0, View arg1, int arg2,
				long arg3) {
			long selected_id = arg0.getItemIdAtPosition(arg2);
			nSelectedBrand = (int) selected_id;
			// String selected_str = arg0.getItemAtPosition(arg2).toString();
			// System.out.println(selected_id + " " + selected_str);
		}

		@Override
		public void onNothingSelected(AdapterView<?> arg0) {
			// TODO Auto-generated method stub

		}
	}

	// class SpinnerPriceListener implements OnItemSelectedListener{
	// @Override
	// public void onItemSelected(AdapterView<?> arg0, View arg1,
	// int arg2, long arg3) {
	// long selected_id = arg0.getItemIdAtPosition(arg2);
	// nSelectedPrice = (int)selected_id;
	// //String selected_str = arg0.getItemAtPosition(arg2).toString();
	// //System.out.println(selected_id + " " + selected_str);
	// }
	// @Override
	// public void onNothingSelected(AdapterView<?> arg0) {
	// // TODO Auto-generated method stub
	// }
	// }

	class SubmitButtionClickListener implements View.OnClickListener {
		@Override
		public void onClick(View v) {
			//友盟统计，搜索
			MobclickAgent.onEvent(SearchActivity.this, "Search");
			
			int brandID = spinner_brand.getSelectedItemPosition();
			int cityID = spinner_city.getSelectedItemPosition()+1;
			// int districtID = spinner_district.getSelectedItemPosition();
			String keyword = keyword_et.getText().toString().trim();
			int minPrice = 0;
			int maxPrice = 0;
			int quality = 0;

			Intent intent = new Intent().setClass(SearchActivity.this,
					MainUI_Single.class);
			intent.putExtra("cityID", cityID);
			intent.putExtra("brandID", brandID);
			intent.putExtra("cityID", cityID);
			intent.putExtra("keyword", keyword);
			try {
				minPrice = Integer.parseInt(min_price_et.getText().toString()
						.trim());
				intent.putExtra("minPrice", minPrice);
			} catch (NumberFormatException e) {
			}
			try {
				maxPrice = Integer.parseInt(max_price_et.getText().toString()
						.trim());
				intent.putExtra("maxPrice", maxPrice);
			} catch (NumberFormatException e) {
			}
			try {
				quality = Integer.parseInt(quality_et.getText().toString()
						.trim());
				intent.putExtra("quality", quality);
			} catch (NumberFormatException e) {
			}

			if (cityID == city_id && brandID == 0 && keyword == ""
					&& minPrice == 0 && maxPrice == 0 && quality == 0) {
				Log.v(TAG, "Search RESULT_CANCELED");
				setResult(RESULT_CANCELED, intent);
			} else {
				Log.v(TAG, "Search RESULT_OK");
				setResult(RESULT_OK, intent);
			}
			finish();
		}
	}

	class CloseButtionClickListener implements View.OnClickListener {
		@Override
		public void onClick(View v) {
			Intent intent = new Intent();
			setResult(RESULT_CANCELED, intent);
			finish();
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