package push800.photograph.utils;

import android.os.Build;
import android.os.Build.VERSION;
import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.PrintStream;

/*
 * 记录日志，只有4个静态方法
 * info,err,warn,debug
 */
public final class Log {

	public static void info(String title, String message) {
		StringBuffer sb = new StringBuffer();
		sb.append("[INFO]");
		sb.append(title);
		sb.append(":");
		sb.append(message);
		System.out.println(sb.toString());
	}
	
	public static void info(String message) {
		StringBuffer sb = new StringBuffer();
		sb.append("[INFO]");
		sb.append(message);
		System.out.println(sb.toString());
	}
	
	public static void err(String title, String message) {
		StringBuffer sb = new StringBuffer();
		sb.append("[ERROR]");
		sb.append(title);
		sb.append(":");
		sb.append(message);
		System.out.println(sb.toString());
	}
	
	public static void err(String message) {
		StringBuffer sb = new StringBuffer();
		sb.append("[ERROR]");
		sb.append(message);
		System.out.println(sb.toString());
	}
	
	public static void warn(String title, String message) {
		StringBuffer sb = new StringBuffer();
		sb.append("[WARNING]");
		sb.append(title);
		sb.append(":");
		sb.append(message);
		System.out.println(sb.toString());
	}
	
	public static void warn(String message) {
		StringBuffer sb = new StringBuffer();
		sb.append("[WARNING]");
		sb.append(message);
		System.out.println(sb.toString());
	}
	
	public static void debug(String title, String message) {
		StringBuffer sb = new StringBuffer();
		sb.append("[DEBUG]");
		sb.append(title);
		sb.append(":");
		sb.append(message);
		System.out.println(sb.toString());
	}
	
	public static void debug(String message) {
		StringBuffer sb = new StringBuffer();
		sb.append("[DEBUG]");
		sb.append(message);
		System.out.println(sb.toString());
	}
}
