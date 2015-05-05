package push800.photograph.login;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.NameValuePair;
import org.apache.http.client.HttpClient;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.message.BasicNameValuePair;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import push800.photograph.R;
import push800.photograph.subscribe.UserCenterActivity;
import push800.photograph.utils.MySQLiteHelper;
import push800.photograph.utils.HttpUtil;
import push800.photograph.utils.Urls;

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.Log;
import android.view.Display;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.view.View.OnClickListener;
import android.view.View.OnFocusChangeListener;
import android.view.WindowManager.LayoutParams;
import android.widget.ArrayAdapter;
import android.widget.AutoCompleteTextView;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.Toast;

public class LoginActivity extends Activity {
	/** Called when the activity is first created. */
	private static String TAG = "LoginActivity";

	// 定义控件变量
	private AutoCompleteTextView et_email = null;
	private EditText et_pw = null;
	private CheckBox cb_remember = null;
	private Button button_regist = null;
	private Button button_login = null;

	private String email = "";
	private String password = "";

	private MySQLiteHelper myDBHelper; // Helper
	private SQLiteDatabase myDB; // 数据库

	private boolean b_email_empty = true;
	private boolean b_pw_empty = true;

	// private int n_UserCounter = -1; // 用户数
	private int n_LastID = -1; // 上一次登录的用户在USERS_LIST中的ID号

	// 网络通信相关的数据
	private String loginBaseUrl = "http://push800.sinaapp.com/frontserver/login/";
	HttpResponse loginHttpResponse;
	private String loginJsonData = "";

	// 在SD卡中存储数据库
	String path_name = "/sdcard/P8PE";
	String file_name = "/sdcard/P8PE/P8PE_db";
	private File path = new File(path_name); // 创建目录
	private File f = new File(file_name); // 创建文件

	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.login);
		
		WindowManager m = getWindowManager();
		Display d = m.getDefaultDisplay(); // 为获取屏幕宽、高
		LayoutParams p = getWindow().getAttributes(); // 获取对话框当前的参数值
		//p.height = (int) (d.getHeight() * 1.0); // 高度设置为屏幕的1.0
		p.width = (int) (d.getWidth() * 0.99); // 宽度设置为屏幕的0.8
		p.alpha = 1.0f; // 设置本身透明度
		p.dimAmount = 0.0f; // 设置黑暗度
		getWindow().setAttributes(p); // 设置生效
		//打开输入键盘了则顶端显示
		getWindow().setGravity(Gravity.TOP);
		
		// 实例化数据库Helper
		myDBHelper = new MySQLiteHelper(this);

		// 创建数据库
		if (!path.exists()) { // 若不存在目录path
			if (path.mkdirs()) // 创建一个目录
				System.out.println("Create Directory Sccessed" + path);
			else
				System.out.println("Create Directory Failed" + path);
		} else
			System.out.println(path + " is existed");

		if (!f.exists()) { // 若不存在文件f
			try {
				f.createNewFile(); // 创建文件
				System.out.println("Create File " + f);
			} catch (IOException e) {
				e.printStackTrace();
			}
		} else
			System.out.println(f + " is existed");

		// 得数据库变量
		myDB = SQLiteDatabase.openOrCreateDatabase(f, null);
		myDBHelper.onCreate(myDB);

		// 得输入控件变量
		button_regist = (Button) findViewById(R.id.button_login_regist);
		button_login = (Button) findViewById(R.id.button_login_login);
		et_email = (AutoCompleteTextView) findViewById(R.id.et_login_id);
		et_pw = (EditText) findViewById(R.id.et_login_pw);
		cb_remember = (CheckBox) findViewById(R.id.cb_login_remember);
		button_login.setEnabled(false);
		cb_remember.setChecked(true);

		// 得上一次登录的账户
		// n_UserCounter = myDBHelper.GetUserCount(myDB);
		// n_LastID = myDBHelper.GetLastID(myDB);
		// System.out.println("last login id is:" + Integer.toString(n_LastID));

		// 从Shared Preferences中读数据-上一次登录的ID号
		SharedPreferences settings = getPreferences(Activity.MODE_PRIVATE);
		n_LastID = settings.getInt("LastLoginID", -1);
		System.out.println(n_LastID);

		// 为id输入框准备自动完成的列表，即得到所有登录过的用户名、Email列表
		List<String> list = new ArrayList<String>();
		Cursor cursor_id = myDBHelper.GetAllID(myDB);
		while (cursor_id.moveToNext()) {
			String strAdd = cursor_id.getString(0);
			list.add(strAdd);
		}
		ArrayAdapter<String> arrayAdapter = new ArrayAdapter<String>(this,
				R.layout.list_item, list);
		et_email.setAdapter(arrayAdapter);

		if (n_LastID > 0) { // 默认显示上一次登录的用户email
			Cursor cursor = myDBHelper.GetUserByID(myDB, n_LastID);
			email = cursor.getString(cursor
					.getColumnIndex(MySQLiteHelper.EMAIL));
			et_email.setText(email);
			b_email_empty = false;
			int isRemember = cursor.getInt(cursor
					.getColumnIndex(MySQLiteHelper.REMEMBER_PW));
			if (isRemember == 1) { // 如果是记住密码，则将密码填上
				password = cursor.getString(cursor
						.getColumnIndex(MySQLiteHelper.PW));
				et_pw.setText(password);
				cb_remember.setChecked(true);
				b_pw_empty = false;
				button_login.setEnabled(true);
			}
		}

		et_email.setOnFocusChangeListener(new OnFocusChangeListener() {

			@Override
			public void onFocusChange(View v, boolean hasFocus) {
				// TODO Auto-generated method stub
				if (hasFocus == false) { // 失去焦点，查该框中的内容是否在库中
											// 如果在，则按是否记住决定是否显示密码
											// 若不在，则清空密码框，记住checkbox勾选
					int nLogin = myDBHelper.IsExistUser(myDB, et_email
							.getText().toString()); // 用户列表中是否有该Email
					// System.out.println("失去焦点" + nLogin);
					if (nLogin == -1) { // 不在，则清空密码框，记住checkbox勾选
						et_pw.setText("");
						cb_remember.setChecked(true);
					} else { // 在，则按是否记住决定是否显示密码
						Cursor cursor = myDBHelper.GetUserByID(myDB, nLogin);
						String temp_pw = cursor.getString(cursor
								.getColumnIndex(MySQLiteHelper.PW));
						et_pw.setText(temp_pw);
						boolean temp_check = cursor.getInt(cursor
								.getColumnIndex(MySQLiteHelper.REMEMBER_PW)) == 1 ? true
								: false;
						cb_remember.setChecked(temp_check);
					}
				}
			}

		});

		// 点击"注册"
		button_regist.setOnClickListener(new OnClickListener() {
			@Override
			public void onClick(View v) {
				email = et_email.getText().toString();
				password = et_pw.getText().toString();

				Intent intent = new Intent();
				// System.out.println("new Intent");
				intent.setClass(LoginActivity.this, RegisterActivity.class);
				// intent.putExtra("email", email);
				// intent.putExtra("pw", password);

				startActivity(intent); // 调用一个新的Activity
			}
		});

		// 点击"登录"
		button_login.setOnClickListener(new OnClickListener() {
			@Override
			public void onClick(View v) {
				email = et_email.getText().toString();
				password = et_pw.getText().toString();
				// System.out.println(email);

				boolean isRemember = cb_remember.isChecked();

				// 将email , password , isRemember三个参数post走
				System.out.println("LoginPost");

				NameValuePair nameValuePairEmail = new BasicNameValuePair(
						"login_id", email);
				NameValuePair nameValuePairPassword = new BasicNameValuePair(
						"password", password);
				List<NameValuePair> param = new ArrayList<NameValuePair>();
				param.add(nameValuePairEmail);
				param.add(nameValuePairPassword);

				JSONObject json = HttpUtil.Post(Urls.LOGIN(), param);
				if (json == null) {
					Log.v(TAG, "createSubscribe response json==null");
				} else {
					// Log.v(TAG, json.toString());
					boolean success = false;
					try {
						success = json.getBoolean("success");
						if (success) {
							// 登陆成功
							Toast.makeText(
									LoginActivity.this.getApplicationContext(),
									"createSubscribe success",
									Toast.LENGTH_SHORT).show();
//							LoginActivity.this.finish();
						} else {
							// 登陆失败
							JSONArray errors = json.getJSONArray("error");
							Toast.makeText(
									LoginActivity.this.getApplicationContext(),
									"createSubscribe failed="
											+ errors.toString(),
									Toast.LENGTH_SHORT).show();
						}
					} catch (JSONException e) {
						e.printStackTrace();
					}
				}

			}
		});

		// 用户名没填时，"登录"按钮不可用
		et_email.addTextChangedListener(new TextWatcher() {
			@Override
			public void afterTextChanged(Editable s) {
				// TODO Auto-generated method stub
			}

			@Override
			public void beforeTextChanged(CharSequence s, int start, int count,
					int after) {
				// TODO Auto-generated method stub
			}

			@Override
			public void onTextChanged(CharSequence s, int start, int before,
					int count) {
				// TODO Auto-generated method stub
				if (s.length() > 0)
					b_email_empty = false;
				else
					b_email_empty = true;

				EnableLogin();
			}
		});

		// 密码没填时，"登录"按钮不可用
		et_pw.addTextChangedListener(new TextWatcher() {
			@Override
			public void afterTextChanged(Editable s) {
				// TODO Auto-generated method stub
			}

			@Override
			public void beforeTextChanged(CharSequence s, int start, int count,
					int after) {
				// TODO Auto-generated method stub
			}

			@Override
			public void onTextChanged(CharSequence s, int start, int before,
					int count) {
				// TODO Auto-generated method stub
				if (s.length() > 0)
					b_pw_empty = false;
				else
					b_pw_empty = true;

				EnableLogin();
			}
		});
	}

	boolean LoginPost(String email, String password, boolean isRemember) { // 将登录信息post，得到服务器的返回值

		// 生成一个请求对象
		HttpPost httpPost = new HttpPost();
		// 生成一个Http客户端对象
		HttpClient httpClient = new DefaultHttpClient();
		// 使用Http客户端发送请求对象
		// httpClient.execute

		// NewValuePair
		NameValuePair nameValuePairEmail = new BasicNameValuePair("login_id",
				email);
		NameValuePair nameValuePairPassword = new BasicNameValuePair(
				"password", password);
		List<NameValuePair> nameValuePairs = new ArrayList<NameValuePair>();
		nameValuePairs.add(nameValuePairEmail);
		nameValuePairs.add(nameValuePairPassword);
		try {
			HttpEntity loginHttpEntity = new UrlEncodedFormEntity(
					nameValuePairs);
			HttpPost loginPost = new HttpPost(loginBaseUrl);
			loginPost.setEntity(loginHttpEntity);
			HttpClient loginHttpClient = new DefaultHttpClient();
			InputStream inputStream = null;
			try {
				loginHttpResponse = loginHttpClient.execute(loginPost);
				loginHttpEntity = loginHttpResponse.getEntity();
				inputStream = loginHttpEntity.getContent();
				BufferedReader reader = new BufferedReader(
						new InputStreamReader(inputStream));
				// String result = "";
				String line = "";
				while ((line = reader.readLine()) != null) {
					loginJsonData = loginJsonData + line;
				}
				// System.out.println("loginJsonData="+loginJsonData);
				JsonLogin jsonLogin = new JsonLogin();
				jsonLogin.parseJason(loginJsonData);
				// jsonLogin.parseJason(inputStream);
			} catch (Exception e) {
				e.printStackTrace();
			}
		} catch (Exception e) {
			e.printStackTrace();
		}

		// 拼url字串，将参数加入
		// String strPostEmail = email;
		// String strPostPassword = password;
		// String strPostUrl = loginBaseUrl + "?email=" + email + "&?assword=" +
		// password;

		return true;
	}

	void EnableLogin() {
		// System.out.println("email:" + b_email_empty);
		// System.out.println("pw" + b_pw_empty);
		if (!b_email_empty && !b_pw_empty)
			button_login.setEnabled(true);
		else
			button_login.setEnabled(false);
	}
}