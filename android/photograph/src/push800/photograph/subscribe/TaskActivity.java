package push800.photograph.subscribe;

import push800.photograph.R;
import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebViewClient;


public class TaskActivity extends Activity {
    /** Called when the activity is first created. */
	
	//	定义控件变量
	WebView mBrowser = null;
	String mStrUrl = "http://push800.sinaapp.com/frontserver/subscribe_list/1/";
	
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.task);
        
    mBrowser = (WebView)findViewById(R.id.wv_task);
    mBrowser.getSettings().setJavaScriptEnabled(true);	//	允许使用JS
    //	点击链接继续在当前browser中响应，而不是新开Android的系统browser中响应该链接
    mBrowser.setWebViewClient(new WebViewClient(){       
        		public boolean shouldOverrideUrlLoading(WebView view, String url) {       
        			view.loadUrl(url);       
        			return true;       
        		}       
    		});
    mBrowser.loadUrl(mStrUrl);
  
    }
}