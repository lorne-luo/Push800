package push800.photograph.subscribe;

import push800.photograph.R;
import push800.photograph.main.MainUI;
import push800.photograph.menu.MenuAdapter;
import push800.photograph.menu.MenuUtils;
import android.app.Activity;
import android.app.Dialog;
import android.app.TimePickerDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.text.format.Time;
import android.util.Log;
import android.view.Gravity;
import android.view.Menu;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemSelectedListener;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.Spinner;
import android.widget.TimePicker;
import android.widget.Toast;


public class SettingActivity extends Activity {
    /** Called when the activity is first created. */
	
	//	定义控件变量
	
	private static final int TIME_FROM_ID = 1;
	private static final int TIME_TO_ID = 2;
	
	private Spinner spinner_push_method = null;
	private Spinner spinner_poll_time = null;
	private Button button_time_start = null;
	private Button button_time_end = null;
	private Button buttonOK = null;
	private Button buttonDefault = null;
	
	int nPushMethodIndex = 0;	//	推送方式序号
	int nPollTimeIndex = 0;		//	轮询时间序号
	int nSelectedPushMethodIndex = 0;	//	选择的推送方式序号
	int nSelectedPollTimeIndex = 0;		//	选择的轮询时间序号
	
	int nTabIndex = 0;
	
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.setting);
        
        Intent intent = getIntent();
        nTabIndex = intent.getIntExtra("CurrentTab",0);
        System.out.println(nTabIndex);
        
        buttonOK = (Button)findViewById(R.id.btn_OK);
        buttonDefault = (Button)findViewById(R.id.btn_Default);
        button_time_start = (Button)findViewById(R.id.btn_time_from);
        button_time_end = (Button)findViewById(R.id.btn_time_to);
        
        spinner_push_method = (Spinner)findViewById(R.id.sp_push_method);
        spinner_poll_time = (Spinner)findViewById(R.id.sp_poll_time);
        
        //	从Shared Preferences中读数据-推送方式和轮询时间间隔的index号
        SharedPreferences settings = getPreferences(Activity.MODE_PRIVATE);
        nPushMethodIndex = settings.getInt("PushMethodIndex", 0);
        System.out.println("推送序号: " + nPushMethodIndex);
        nPollTimeIndex = settings.getInt("PollTimeIndex", 0);
        System.out.println("轮询时间序号: " + nPollTimeIndex);
        
        //	为所选项赋初值，为写回Shared Preferences做准备
        nSelectedPushMethodIndex = nPushMethodIndex;
        nSelectedPollTimeIndex = nPollTimeIndex;
        
        //	为推送方式创建Adapter
        ArrayAdapter<CharSequence> adapter_push_method = ArrayAdapter.createFromResource(
        		this,
        		R.array.mathod_list,
        		android.R.layout.simple_spinner_item);
        spinner_push_method.setAdapter(adapter_push_method);
        spinner_push_method.setPrompt("请选择推送方式");
        spinner_push_method.setOnItemSelectedListener(new SpinnerMethodOnSelectedListener());
        spinner_push_method.setSelection(nPushMethodIndex);
        
        
        //	为轮询时间创建Adapter
        ArrayAdapter<CharSequence> adapter_poll_time = ArrayAdapter.createFromResource(
        		this, R.array.polltime_list, android.R.layout.simple_spinner_item);
        spinner_poll_time.setAdapter(adapter_poll_time);
        spinner_poll_time.setPrompt("请选择查询间隔");
        spinner_poll_time.setOnItemSelectedListener(new SpinnerPollTimeOnSelectedListener());        
        spinner_poll_time.setSelection(nPollTimeIndex);
        
        button_time_start.setOnClickListener(new TimeStartListener());
        button_time_end.setOnClickListener(new TimeEndListener());
        buttonOK.setOnClickListener(new OKListener());
        buttonDefault.setOnClickListener(new DefaultListener());
    }
    
    //	"默认"按钮的监听器
    private class DefaultListener implements OnClickListener
    {

		@Override
		public void onClick(View v) {
			// TODO Auto-generated method stub
			nSelectedPushMethodIndex = 0;
			nSelectedPollTimeIndex = 0;
			spinner_push_method.setSelection(0);
			spinner_poll_time.setSelection(0);
		}
    	
    }
    
    //	"确定"按钮的监听器
    private class OKListener implements OnClickListener
    {

		@Override
		public void onClick(View v) {
			// TODO Auto-generated method stub
			//	向Shared Preferences写数据做准备，得Editor
			SharedPreferences uiState = getPreferences(0);
			SharedPreferences.Editor editor = uiState.edit();
			//	向Shared Preferences写数据
			editor.putInt("PushMethodIndex", nSelectedPushMethodIndex);
			editor.putInt("PollTimeIndex" , nSelectedPollTimeIndex);
			editor.commit();
			//	回到用户主界面
			BackToUserPage();
		}
    	
    }
    
    void BackToUserPage()
    {
    	Toast toast = Toast.makeText(SettingActivity.this, "设置已更新",
				Toast.LENGTH_LONG);
/*    	System.out.println("nTabIndex = " + nTabIndex);
    	String str = Integer.toString(nTabIndex);
    	Intent intent = new Intent();
    	intent.putExtra("TabIndex", str);
    	System.out.println(str);
    	intent.setClass(SettingActivity.this, UserTabActivity.class);
    	startActivity(intent);
    	return;
*/
    }
    
    
    private class TimeStartListener implements OnClickListener{

		@Override
		public void onClick(View v) {
			// TODO Auto-generated method stub
			//	用于显示TimePickerDialog
			showDialog(TIME_FROM_ID);
		}
    }
    
    private class TimeEndListener implements OnClickListener{

		@Override
		public void onClick(View v) {
			// TODO Auto-generated method stub
			//	用于显示TimePickerDialog
			showDialog(TIME_TO_ID);
		}
    }
    
    //	监听器，监听用户点下按钮TimePickerDialog的set按钮时，所设置的时间
    TimePickerDialog.OnTimeSetListener onTimeStartSetListener = new TimePickerDialog.OnTimeSetListener() {
		
		@Override
		public void onTimeSet(TimePicker view, int hourOfDay, int minute) {
			// TODO Auto-generated method stub
			//System.out.println(hourOfDay + " : " + minute + " start");
			String str = "";
			if(minute > 9)
				str = Integer.toString(hourOfDay) + ":" + Integer.toString(minute);
			else
				str = Integer.toString(hourOfDay) + ":0" + Integer.toString(minute);
			button_time_start.setText(str);
		}
	};
	
	
	 //	监听器，监听用户点下按钮TimePickerDialog的set按钮时，所设置的时间
    TimePickerDialog.OnTimeSetListener onTimeEndSetListener = new TimePickerDialog.OnTimeSetListener() {
		
		@Override
		public void onTimeSet(TimePicker view, int hourOfDay, int minute) {
			// TODO Auto-generated method stub
			//System.out.println(hourOfDay + " : " + minute + " end");
			String str = "";
			if(minute > 9)
				str = Integer.toString(hourOfDay) + ":" + Integer.toString(minute);
			else
				str = Integer.toString(hourOfDay) + ":0" + Integer.toString(minute);
			
			Time time = new Time();
			time.hour = hourOfDay;
			time.minute = minute;
			System.out.println(time);
			button_time_end.setText(str);
		}
	};
	

	@Override
	protected Dialog onCreateDialog(int id) {
		// TODO Auto-generated method stub
		switch(id){
		case TIME_FROM_ID:
			return new TimePickerDialog(this , onTimeStartSetListener , 8 , 0 , true);
		case TIME_TO_ID:
			return new TimePickerDialog(this , onTimeEndSetListener , 23 , 30 , true);
		}
		//return super.onCreateDialog(id);
		return null;
	}
	
	
	
	
	class SpinnerMethodOnSelectedListener implements OnItemSelectedListener{

		@Override
		public void onItemSelected(AdapterView<?> arg0, View arg1,
				int arg2, long arg3) {
			// TODO Auto-generated method stub
			long selected_id = arg0.getItemIdAtPosition(arg2);
			nSelectedPushMethodIndex = (int)selected_id;
			//String selected_str = arg0.getItemAtPosition(arg2).toString();
			//System.out.println(selected_id + " " + selected_str);
		}

		@Override
		public void onNothingSelected(AdapterView<?> arg0) {
			// TODO Auto-generated method stub
			
		}
    }
	
	class SpinnerPollTimeOnSelectedListener implements OnItemSelectedListener{

		@Override
		public void onItemSelected(AdapterView<?> arg0, View arg1, int arg2,
				long arg3) {
			// TODO Auto-generated method stub
			long selected_id = arg0.getItemIdAtPosition(arg2);
			nSelectedPollTimeIndex = (int)selected_id;
			//String selected_str = arg0.getItemAtPosition(arg2).toString();
			//System.out.println(selected_id + " " + selected_str);
		}

		@Override
		public void onNothingSelected(AdapterView<?> arg0) {
			// TODO Auto-generated method stub
			
		}
		
	}
	
	@Override
	//弹出菜单的逻辑
	public boolean onMenuOpened(int featureId, Menu menu) {
		MainUI.menulists = null;
		if (MainUI.popup != null) {
			//这里设置菜单项
			MainUI.menulists = MenuUtils.getSettingList();

			MainUI.menuAdapter = new MenuAdapter(this, MainUI.menulists);
			MainUI.menuGridView.setAdapter(MainUI.menuAdapter);
			MainUI.popup.showAtLocation(this.findViewById(R.id.setting_linearlayout),
					Gravity.BOTTOM, 0, 0);
		}
		return false;
		// return super.onMenuOpened(featureId, menu);
	}
}