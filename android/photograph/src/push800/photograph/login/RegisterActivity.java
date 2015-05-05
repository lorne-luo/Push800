package push800.photograph.login;

import push800.photograph.R;
import push800.photograph.utils.DialogFactory;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.os.Bundle;
import android.view.Display;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.view.View.OnClickListener;
import android.view.WindowManager.LayoutParams;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemSelectedListener;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.Spinner;
import android.widget.TextView;
//import android.widget.CheckBox;
import android.widget.EditText;

public class RegisterActivity extends Activity {
    /** Called when the activity is first created. */
	
	//	定义控件变量
	//private EditText et_email = null;
	//private EditText et_pw = null;
	private Button submitBtn=null;
	private Spinner citySpinner = null;

	
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.register);
        
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
		
        //et_email = (EditText)findViewById(R.id.et_regist_id);
        //et_pw = (EditText)findViewById(R.id.et_regist_pw);
        
        submitBtn = (Button)findViewById(R.id.btn_regist);
        citySpinner=(Spinner)findViewById(R.id.sp_regist_city);
        initCitySpinner();

        //Intent intent = getIntent();
        //String email = (String)intent.getStringExtra("email");
        //String password = (String)intent.getStringExtra("pw");
        //System.out.println(email + password);
        //et_email.setText(email);
        //et_pw.setText(password);
        
        
        
        submitBtn.setOnClickListener(new OnClickListener()
        {
			@Override
			public void onClick(View v) {
				try {
					String email = ((EditText)findViewById(R.id.et_regist_id)).getText().toString();
					String pwd=((EditText)findViewById(R.id.et_regist_pw)).getText().toString();
					String pwd_confirm = ((EditText)findViewById(R.id.et_regist_confirm_pw)).getText().toString();
					if (pwd!=pwd_confirm){
						AlertDialog ad=DialogFactory.getAlert(RegisterActivity.this,"密码输入不一致","");
						ad.show();
					}
					String username=((EditText)findViewById(R.id.et_regist_username)).getText().toString();
					String phone_num=((EditText)findViewById(R.id.et_regist_tel)).getText().toString();
					//String city_id=((Spinner)findViewById(R.id.sp_regist_city)).get
					
					System.out.println("email="+email);
					System.out.println("pwd="+pwd);
					
				} catch (Exception e) {
					System.out.println(e.getClass().getName()+"="+e.getMessage());
				}
			}
        });
        
        
    }

    private void initCitySpinner() {
		ArrayAdapter<CharSequence> adapter = ArrayAdapter.createFromResource(
                this, R.array.city_list,
                android.R.layout.simple_spinner_item);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        citySpinner.setAdapter(adapter);
        citySpinner.setPrompt("请选择城市");
        citySpinner.setOnItemSelectedListener(new SpinnerOnSelectedListener());
	}
    
	class SpinnerOnSelectedListener implements OnItemSelectedListener{
		@Override
		public void onItemSelected(AdapterView<?> adapterView, View view, int position,
                long id) {
			// TODO Auto-generated method stub
			String selected = adapterView.getItemAtPosition(position).toString();
            System.out.println("selected===========>" + selected);
		}

		@Override
		public void onNothingSelected(AdapterView<?> arg0) {
			// TODO Auto-generated method stub
			System.out.println("selected===========>" + "Nothing");
		}
    }

}