package push800.photograph.utils;

import android.content.Context;
import android.widget.Toast;

public class ToastUtil
{
  private static Toast toast;

  public static void cancelAndShowToast(Toast paramToast)
  {
    if (paramToast != null)
    {
      paramToast.cancel();
      paramToast.show();
    }
  }

  public static void cancelToast(Toast paramToast)
  {
    if (paramToast != null)
      paramToast.cancel();
  }

  public static void showToast(int paramInt1, int paramInt2)
  {
    //showToast(QQPimUtils.APPLICATION_CONTEXT.getString(paramInt1), paramInt2);
  }

  public static void showToast(String paramString, int paramInt)
  {
//    if (toast == null)
//      toast = Toast.makeText(getApplicationContext(), "", 0);
    toast.cancel();
    toast.setText(paramString);
    toast.setDuration(paramInt);
    toast.setGravity(81, 0, 50);
    toast.show();
  }

  public static void showToast(String paramString, int paramInt1, int paramInt2)
  {
    //if (toast == null)
      //toast = Toast.makeText(QQPimUtils.APPLICATION_CONTEXT, "", 0);
    toast.cancel();
    toast.setText(paramString);
    toast.setDuration(paramInt1);
    toast.setGravity(paramInt2, 0, 0);
    toast.show();
  }
}
