package push800.photograph.main;

import java.lang.reflect.Method;
import java.util.Date;

import push800.photograph.R;
import android.app.Activity;
import android.app.Dialog;
import android.app.ProgressDialog;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.util.Log;
import android.view.KeyEvent;
import android.view.View;
import android.view.Window;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.TextView;
import android.widget.Toast;

public class BrowserUI extends Activity {
	private WebView webView = null;
	private ProgressDialog dialog = null;

	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		// 设置特性以允许在应用程序的标题栏上显示进度条（条状）
		requestWindowFeature(Window.FEATURE_PROGRESS);
		// 设置特性以允许在应用程序的标题栏上显示进度条（圆圈状）
		requestWindowFeature(Window.FEATURE_INDETERMINATE_PROGRESS);
		setContentView(R.layout.webview);

		setTitle("首页");
		// 在标题栏上显示进度条（条状）
		setProgressBarVisibility(true);
		// 在标题栏上显示进度条（圆圈状）
		setProgressBarIndeterminateVisibility(true);
		
		initView();
	}

	// 初始化窗口
	private void initView() {
		this.webView = (WebView) findViewById(R.id.webview);
		WebSettings settings = webView.getSettings();
		settings.setJavaScriptEnabled(true);
		settings.setSupportMultipleWindows(false);
		settings.setJavaScriptCanOpenWindowsAutomatically(false);
		settings.setPluginsEnabled(true);
		settings.setUserAgent(0);// 手机用户

		webView.setWebViewClient(new MyClient());
		webView.setWebChromeClient(new MyChromeClient());

		// webView.requestFocus();
		webView.loadUrl("http://push800.sinaapp.com/frontserver/message/1/38850/");
	}

	@Override
	// 设置回退
	public boolean onKeyDown(int keyCode, KeyEvent event) {
		if ((keyCode == KeyEvent.KEYCODE_BACK) && webView.canGoBack()) {
			webView.goBack();
			return true;
		}
		return super.onKeyDown(keyCode, event);
	}

	@Override
	protected Dialog onCreateDialog(int id) {
		// 实例化进度条对话框
		dialog = new ProgressDialog(this);
		dialog.setTitle("正在加载，请稍候！");
		dialog.setIndeterminate(true);
		dialog.setMessage("正在加载，请稍候！");
		dialog.setCancelable(true);
		return dialog;
	}

	//自定义的WebViewClient
	private class MyClient extends WebViewClient {
		@Override
		// 只能捕捉到程序中loadurl的访问，用户的点击要用onPageStarted来截获
		public boolean shouldOverrideUrlLoading(WebView view, String url) {
			webView.loadUrl(url);
			return (true);
		}

		public void onProgressChanged(WebView view, int newProgress) {
			// activity的进度是0 to 10000 (both inclusive),所以要*100
			BrowserUI.this.setProgress(newProgress * 100);
		}

		@Override
		// 页面开始加载
		public void onPageStarted(WebView view, String url, Bitmap favicon) {
			Toast.makeText(getApplicationContext(), url, Toast.LENGTH_SHORT)
					.show();
			if (!url.startsWith("http://www")) {
				// webView.stopLoading();
			}
		}

		@Override
		// 页面完成加载
		public void onPageFinished(WebView view, String url) {
			if (dialog != null) {
				dialog.dismiss();
			}
		}

		@Override
		public void onReceivedError(WebView view, int errorCode,
				String description, String failingUrl) {
			// TODO Auto-generated method stub
			super.onReceivedError(view, errorCode, description, failingUrl);
			if (dialog != null) {
				dialog.dismiss();
			}
		}
		
		 

		private void setEmbeddedTitleBar(WebView web, View titlebar) {
			try {
				Method m = WebView.class.getMethod("setEmbeddedTitleBar",
						new Class[] { View.class });
				m.invoke(web, titlebar);
			} catch (Exception e) {
				Log.d("TEST", "Err: " + e.toString());
			}
		}
	}
	
	//自定义的WebChromeClient
	//WebChromeClient提供progress的操作
	private class MyChromeClient extends WebChromeClient {
		@Override 
		public void onProgressChanged(WebView view, int newProgress) {
			// activity的进度是0 to 10000 (both inclusive),所以要*100
			setProgress(newProgress * 100);
		}
		@Override 
        public void onReceivedTitle(WebView view, String title) { 
            //设置当前activity的标题栏 
			BrowserUI.this.setTitle(title); 
            super.onReceivedTitle(view, title); 
        }
	}
}
	
