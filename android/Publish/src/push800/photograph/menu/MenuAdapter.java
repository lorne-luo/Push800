package push800.photograph.menu;

import java.util.List;

import push800.photograph.menu.MenuInfo;
import push800.photograph.R;
import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.ImageView;
import android.widget.TextView;

public class MenuAdapter extends BaseAdapter {

	private final List<MenuInfo> list;
	private final LayoutInflater inflater;
	public MenuAdapter(Context context,List<MenuInfo> list){
		this.list=list;
		inflater=LayoutInflater.from(context);
	}
	
	public int getCount() {
		// TODO Auto-generated method stub
		return list.size();
	}

	public Object getItem(int arg0) {
		// TODO Auto-generated method stub
		return list.get(arg0);
	}

	public long getItemId(int arg0) {
		// TODO Auto-generated method stub
		return arg0;
	}

	public View getView(int arg0, View arg1, ViewGroup arg2) {
		// TODO Auto-generated method stub
		View view=arg1;
		if (view==null) {
			view=inflater.inflate(R.layout.menu_item, null);
		}
		MenuInfo mInfo=list.get(arg0);
		ImageView iView=(ImageView)view.findViewById(R.id.menu_item_image);
		TextView tView=(TextView)view.findViewById(R.id.menu_item_text);
		iView.setImageResource(mInfo.imgsrc);
		tView.setText(mInfo.title);
		if (mInfo.ishide) {			
			iView.setAlpha(80);
		}
		return view;
	}

}
