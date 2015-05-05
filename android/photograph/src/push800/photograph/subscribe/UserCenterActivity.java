package push800.photograph.subscribe;

import push800.photograph.R;
import push800.photograph.main.MsgActivity;
import android.app.AlertDialog;
import android.app.TabActivity;
import android.content.DialogInterface;
import android.content.Intent;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.TabHost;
import android.widget.TabHost.OnTabChangeListener;

public class UserCenterActivity extends TabActivity {
    /** Called when the activity is first created. */
	
	TabHost mTabHost = null;
	int nCurrentTab = 1;
	
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.tabhost);
        System.out.println("UserTabActivity");
        Intent intent = getIntent();
        String strCurrentTab = intent.getStringExtra("CurrentTab");
        nCurrentTab = Integer.valueOf(strCurrentTab);
        //System.out.println(nCurrentTab);
        
        //	取得TabHost
        mTabHost = getTabHost();
        
        //	创建intent
        Intent intent_task = new Intent();
        intent_task.setClass(UserCenterActivity.this , TaskActivity.class);
        
        Intent intent_submit = new Intent();
        intent_submit.setClass(UserCenterActivity.this , SubmitActivity.class);
        
        Intent intent_msg = new Intent();
        intent_msg.setClass(UserCenterActivity.this , MsgActivity.class);
        
 
        //	为TabHost添加标签
        //	创建一个NewTabSpec(newTabSpec)
        //	设置其标签和图标(setIndicator)
        //	设置内容(setContent)
        
        mTabHost.addTab(mTabHost.newTabSpec("tab_task")
        		.setIndicator("TAB_1" , getResources().getDrawable(R.drawable.tab_index))
        		.setContent(intent_task));
        mTabHost.addTab(mTabHost.newTabSpec("tab_submit")
        		.setIndicator("TAB_2" , getResources().getDrawable(R.drawable.tab_settings))
        		.setContent(intent_submit));
        mTabHost.addTab(mTabHost.newTabSpec("tab_msg")
        		.setIndicator("TAB_3" , getResources().getDrawable(R.drawable.tab_subscribe))
        		.setContent(intent_msg));
        
        //	设置TabHost的背景颜色
        //mTabHost.setBackgroundColor(Color.argb(150, 22, 70, 150));
        
        //	设置TabHost的背景图片资源
        //mTabHost.setBackgroundResource(R.drawable.bg0);
        
        //	设置当前显示哪一个标签
        mTabHost.setCurrentTab(nCurrentTab);
        
        //	切换标签事件处理
        mTabHost.setOnTabChangedListener(new OnTabChangeListener()
        {

			@Override
			public void onTabChanged(String tabId) {
				// TODO Auto-generated method stub
//				Dialog dialog = new AlertDialog.Builder(UserTabActivity.this)
//					.setTitle("提示")
//					.setMessage("当前选中: " + tabId + "标签")
//					.setPositiveButton("确定" , 
//					new DialogInterface.OnClickListener()
//					{
//						public void onClick(DialogInterface dialog , int whichButton)
//						{
//							dialog.cancel();
//						}
//					}).create();	//	创建按钮
//				dialog.show();
			}
        });
    }

    //	按MENU键
	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// TODO Auto-generated method stub
		nCurrentTab = mTabHost.getCurrentTab();
		menu.add(0 , 1 , 1 , R.string.menu_exit);
		menu.add(0 , 2 , 2 , R.string.menu_useage);
		menu.add(0 , 3 , 3 , R.string.menu_about);
		menu.add(0 , 4 , 4 , R.string.menu_about);
		return super.onCreateOptionsMenu(menu);
	}

	//	点选MENU弹出的菜单项
	@Override
	public boolean onOptionsItemSelected(MenuItem item) {
		// TODO Auto-generated method stub
		switch(item.getItemId())
		{
		case 1:	//	退出
			break;
			
		case 2:	//	说明
			break;
			
		case 3:	//	关于
			displayAbout();
			break;
			
		case 4:	//	设置
			Intent intent_setting = new Intent();
			intent_setting.putExtra("CurrentTab", Integer.toString(nCurrentTab));
			intent_setting.setClass(UserCenterActivity.this , SettingActivity.class);
			startActivity(intent_setting);
			break;
		}
		
		return super.onOptionsItemSelected(item);
	}
	
	
	
	
	public void displayAbout()
    {	//	显示关于信息
		System.out.println("display about");
    	new AlertDialog.Builder(UserCenterActivity.this)
		.setTitle(R.string.menu_about)
		.setMessage(R.string.about_tips)
		.setPositiveButton(
				R.string.app_ISee, 
				new DialogInterface.OnClickListener()
				{
					public void onClick(DialogInterface dialoginterface , int i)
					{
						//	Do Nothing
					}
				}
		)
		.show();
    	return;
    }
	
	
    
    
    
}