package push800.photograph.utils;

import push800.photograph.R;

import android.app.AlertDialog;
import android.app.AlertDialog.Builder;
import android.app.ProgressDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.res.Resources;

public class DialogFactory {
	public static AlertDialog getAlert(Context paramContext, int paramInt1,
			int paramInt2) {
		String str1 = paramContext.getString(paramInt1);
		String str2 = paramContext.getString(paramInt2);
		return getAlert(paramContext, str1, str2);
	}

	public static AlertDialog getAlert(Context paramContext,
			String paramString1, String paramString2) {
		AlertDialog.Builder localBuilder = new AlertDialog.Builder(paramContext)
				.setTitle(paramString1).setMessage(paramString2)
				.setCancelable(true);
		String str = paramContext.getString(R.string.setting_OK);
		return localBuilder.setNeutralButton(str,
				new DialogInterface.OnClickListener() {
					public void onClick(DialogInterface paramDialogInterface,
							int paramInt) {
						paramDialogInterface.dismiss();
					}
				}).create();
	}

	public static AlertDialog getConfirmAlert(Context paramContext,
			String title, String content,
			DialogInterface.OnClickListener listener) {

		AlertDialog.Builder localBuilder = new AlertDialog.Builder(paramContext)
				.setTitle(title).setMessage(content).setCancelable(true);
		localBuilder.setPositiveButton("是",listener);
		localBuilder.setNegativeButton("否",
				new DialogInterface.OnClickListener() {
					public void onClick(DialogInterface dialog, int id) {
						dialog.cancel();
					}
				});
		return localBuilder.create();
	}

	public static ProgressDialog getProgressDialog(Context paramContext,
			String paramString1, String paramString2) {
		ProgressDialog localProgressDialog = new ProgressDialog(paramContext);
		localProgressDialog.setTitle(paramString1);
		localProgressDialog.setMessage(paramString2);
		return localProgressDialog;
	}

	public static ProgressDialog showProgressDialog(Context paramContext,
			int paramInt1, int paramInt2) {
		String str1 = paramContext.getString(paramInt1);
		String str2 = paramContext.getString(paramInt2);
		return ProgressDialog.show(paramContext, str1, str2);
	}

}