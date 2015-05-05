package push800.photograph.subscribe;

//import dqq.p8pe.SettingActivity.SpinnerMethodOnSelectedListener;
import java.util.ArrayList;
import java.util.List;

import org.apache.http.NameValuePair;
import org.apache.http.message.BasicNameValuePair;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import push800.photograph.R;
import push800.photograph.main.MainUI;
import push800.photograph.menu.MenuAdapter;
import push800.photograph.menu.MenuInfo;
import push800.photograph.menu.MenuUtils;
import push800.photograph.utils.City;
import push800.photograph.utils.Urls;
import push800.photograph.utils.HttpUtil;
import android.R.integer;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.Gravity;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.Toast;
import android.widget.AdapterView.OnItemSelectedListener;

public class SubmitActivity extends Activity {
	private static String TAG = "SubmitActivity";

	// 定义控件变量
	private Spinner spinner_city = null;
	private Spinner spinner_district = null;
	private Spinner spinner_brand = null;
	// private Spinner spinner_price = null;
	private Button submit_btn = null;
	private EditText min_price_et = null;
	private EditText max_price_et = null;
	private EditText keyword_et = null;

	// 定义变量
	private int nSelectedCity = 0;
	private int nSelectedDistrict = 0;
	private int nSelectedBrand = 0;
	// private int nSelectedPrice = 0;
	ArrayAdapter<CharSequence> adapter_district = null;

	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.submit);

		// 得到控件对象
		spinner_city = (Spinner) findViewById(R.id.sp_city);
		spinner_district = (Spinner) findViewById(R.id.sp_district);
		spinner_brand = (Spinner) findViewById(R.id.sp_brand);
		submit_btn = (Button) findViewById(R.id.submit_btn);
		min_price_et = (EditText) findViewById(R.id.min_price_et);
		max_price_et = (EditText) findViewById(R.id.max_price_et);
		keyword_et = (EditText) findViewById(R.id.keyword_et);
		// spinner_price = (Spinner)findViewById(R.id.sp_price);

		// 为"城市"创建Adapter
		ArrayAdapter<CharSequence> adapter_city = ArrayAdapter
				.createFromResource(this, R.array.city_list,
						android.R.layout.simple_spinner_item);
		spinner_city.setAdapter(adapter_city);
		spinner_city.setPrompt("请选择城市");
		spinner_city.setOnItemSelectedListener(new SpinnerCityListener());
		spinner_city.setSelection(0);

		// 为"品牌"创建Adapter
		ArrayAdapter<CharSequence> adapter_brand = ArrayAdapter
				.createFromResource(this, R.array.brand_list,
						android.R.layout.simple_spinner_item);
		spinner_brand.setAdapter(adapter_brand);
		spinner_brand.setPrompt("请选择品牌");
		spinner_brand.setOnItemSelectedListener(new SpinnerBrandListener());
		spinner_brand.setSelection(0);

		// 在未选择城市之前，城区的spinner显示出城区两个字
		String[] district = new String[] { "城区" };
		ArrayAdapter<String> adapter = new ArrayAdapter<String>(this,
				android.R.layout.simple_spinner_item, district);
		spinner_district.setPrompt("请先选择城市");
		spinner_district.setAdapter(adapter);

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
	}

	@Override
	//弹出菜单的逻辑
	public boolean onMenuOpened(int featureId, Menu menu) {
		MainUI.menulists = null;
		if (MainUI.popup != null) {
			//这里设置菜单项
			MainUI.menulists = MenuUtils.getUserCenterList();

			MainUI.menuAdapter = new MenuAdapter(this, MainUI.menulists);
			MainUI.menuGridView.setAdapter(MainUI.menuAdapter);
			MainUI.popup.showAtLocation(this.findViewById(R.id.submit_linearlayout),
					Gravity.BOTTOM, 0, 0);
		}
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
				if (adapter_district != null)
					spinner_district.setSelection(0);
				spinner_district.setEnabled(false);
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
			spinner_district.setEnabled(true);

			// 为"城区"创建Adapter
			// if(adapter_district != null)
			// adapter_district.clear();

			adapter_district = ArrayAdapter.createFromResource(
					SubmitActivity.this, ID_DISTRICT_LIST,
					android.R.layout.simple_spinner_item);
			spinner_district.setAdapter(adapter_district);
			spinner_district.setPrompt("请选择城区");
			spinner_district
					.setOnItemSelectedListener(new SpinnerDistrictListener());
			spinner_district.setSelection(0);
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
			int brandID = spinner_brand.getSelectedItemPosition();
			int cityID = spinner_city.getSelectedItemPosition();
			int districtID = spinner_district.getSelectedItemPosition();
			String keyword = keyword_et.getText().toString();
			String minPrice = min_price_et.getText().toString();
			String maxPrice = max_price_et.getText().toString();

			// Toast.makeText(SubmitActivity.this.getApplicationContext(),
			// "districtID="+districtID, Toast.LENGTH_SHORT).show();

			List<NameValuePair> param = new ArrayList<NameValuePair>();
			// business_id作为常量保存在了程序里
			param.add(new BasicNameValuePair("business_id", getResources()
					.getString(R.string.business_id)));
			param.add(new BasicNameValuePair("city_id", String.valueOf(cityID)));
			param.add(new BasicNameValuePair("brand_id", String
					.valueOf(brandID)));
			param.add(new BasicNameValuePair("district_id", String
					.valueOf(districtID)));
			param.add(new BasicNameValuePair("keyword", keyword));
			// param.add(new BasicNameValuePair("min_price", price));
			param.add(new BasicNameValuePair("min_price", minPrice));
			param.add(new BasicNameValuePair("max_price", maxPrice));
			param.add(new BasicNameValuePair("login_id", "push800@sina.com"));
			param.add(new BasicNameValuePair("user_token", "6.20565686525"));
			JSONObject json = HttpUtil.Post(Urls.SUBMIT_SUBSCRIBE(), param);
			if (json == null) {
				Log.v(TAG, "createSubscribe response json==null");
			} else {
				// Log.v(TAG, json.toString());
				boolean success = false;
				try {
					success = json.getBoolean("success");
					if (success) {
						Toast.makeText(
								SubmitActivity.this.getApplicationContext(),
								"createSubscribe success", Toast.LENGTH_SHORT)
								.show();
					} else {
						JSONArray errors = json.getJSONArray("error");
						Toast.makeText(
								SubmitActivity.this.getApplicationContext(),
								"createSubscribe failed=" + errors.toString(),
								Toast.LENGTH_SHORT).show();
					}
				} catch (JSONException e) {
					e.printStackTrace();
				}
			}
		}
	}

}