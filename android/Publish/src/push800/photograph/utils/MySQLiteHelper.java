package push800.photograph.utils;



import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.database.sqlite.SQLiteDatabase.CursorFactory;

public class MySQLiteHelper extends SQLiteOpenHelper{

	public final static String DATABASE_NAME = "P8PE_db";	//	数据库名
	public final static int VERSION = 1;	//	版本号
	public final static String USERS_LIST = "USERS_LIST";	//	用户列表的表名
	public final static String ID = "_id";
	public final static String EMAIL = "email";
	public final static String PW = "pw";
	public final static String REMEMBER_PW = "remember_pw";
	
	public final static String LAST_LOGIN = "LAST_LOGIN";	//	记录上次登录的表，仅1行
	public final static String LAST_LOGIN_ID = "last_id";	//	上次登录的用户在USERS_LIST中的

//	public final static String DISHES_NAME = "dishes_name";
//	public final static String DISHES_PRICE = "dishes_price";
	
	
	public MySQLiteHelper(Context context, String name, CursorFactory factory,
			int version) {
		super(context, name, factory, version);
		// TODO Auto-generated constructor stub
	}
	
	public MySQLiteHelper(Context context)
	{
		super(context, DATABASE_NAME, null, VERSION);
		// TODO Auto-generated constructor stub
	}


	@Override
	public void onCreate(SQLiteDatabase db) {
		// TODO Auto-generated method stub
	
		//	检查是否有USERS_LIST表
		boolean IsNeedCreate = true;
		Cursor cursor = null;
		try{
			String sql = "select count(*) as c from sqlite_master where type = 'table' and name ='"+USERS_LIST.trim()+"' ";
			//System.out.println(sql);
			cursor = db.rawQuery(sql , null);
			if(cursor.moveToNext()){
				int count = cursor.getInt(0);
				//System.out.println(count);
				if(count > 0){
					//	有指定的表
					//System.out.println("USERS_LIST 表中有内容，IsNeedCreate = false");
					IsNeedCreate = false;
				}
			}
		}catch(Exception e){
			
		}
		
		if(IsNeedCreate)
		{
			String str_sql = "CREATE TABLE " + USERS_LIST + "(" + ID 
			+ " INTEGER PRIMARY KEY AUTOINCREMENT , " + EMAIL + " text , " + PW + " text , " + REMEMBER_PW + " INTEGER);";
			
			db.execSQL(str_sql);
			//System.out.println("Create \"USERS_LIST\" table");
		}
		
		
//		检查是否有LAST_LOGIN表
		IsNeedCreate = true;
		cursor = null;
		
		try{
			String sql = "select count(*) as c from sqlite_master where type = 'table' and name ='"+LAST_LOGIN.trim()+"' ";
			//System.out.println(sql);
			cursor = db.rawQuery(sql , null);
			if(cursor.moveToNext()){
				int count = cursor.getInt(0);
				//System.out.println(count);
				if(count > 0){
					//	有指定的表
					//System.out.println("LAST_LOGIN 表中有内容，IsNeedCreate = false");
					IsNeedCreate = false;
				}
			}
		}catch(Exception e){
			
		}
		
		if(IsNeedCreate)
		{
			String str_sql = "CREATE TABLE " + LAST_LOGIN + "(" + ID 
			+ " INTEGER PRIMARY KEY , " + LAST_LOGIN_ID + " INTEGER);";
			
			db.execSQL(str_sql);
			//System.out.println("Need to Create \"LAST_LOGIN\" table");
		}
	}


	@Override
	public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
		// TODO Auto-generated method stub
		System.out.println("Upgrade DataBase");
	}
	
	public void test(){
		System.out.println("helper.test...");
	}
	
	public Cursor query(SQLiteDatabase db , String sql , String[] args)
	{
		//SQLiteDatabase db = this.getReadableDatabase();		
		Cursor cursor = db.rawQuery(sql, args);
		return cursor;
	}
	
	public Cursor select(SQLiteDatabase db) 
	{ 
	    Cursor cursor = db.query(USERS_LIST, null, null, null, null, null, null);
	    return cursor;
	}
	
	public Cursor select(SQLiteDatabase db , String table_name) 
	{ 
	    Cursor cursor = db.query(table_name, null, null, null, null, null, null);
	    return cursor;
	}
	
	
	public int GetUserCount(SQLiteDatabase db)
	{	//	得到用户数
		int i = -1;
		String sql = "select * from " + USERS_LIST + ";";
//		System.out.println(sql);
		Cursor cursor = db.rawQuery(sql , null);
		if(cursor != null)
		{
//			System.out.println("not null");
			i = cursor.getCount();
		}
//		else
//			System.out.println("null");
		return i;
	}
	
	int GetLastID(SQLiteDatabase db)
	{	//	返回上次登录的ID编号
		int ret = -1;
		Cursor cursor = null;
		cursor = db.query(LAST_LOGIN , new String[]{LAST_LOGIN_ID} , ID + "=?" , new String[]{"1"} , null , null , null);
		cursor.moveToNext();
		ret = cursor.getInt(cursor.getColumnIndex(LAST_LOGIN_ID));
		return ret;
	}
	
	public Cursor GetUserByID(SQLiteDatabase db , int num)
	{	//	返回_id=num的账户信息
		Cursor cursor = null;
		cursor = db.query(USERS_LIST , null, ID + "=?" , new String[]{Integer.toString(num)} , null, null, null);
		cursor.moveToFirst();
		return cursor;
	}
	
	
	public Cursor GetAllID(SQLiteDatabase db)
	{	//	返回所有登录过的用户名
		Cursor cursor = null;
		cursor = db.query(USERS_LIST , new String[]{"EMAIL"} , null, null, null, null, null);
		return cursor;
	}
	
	
	
	public int IsExistUser(SQLiteDatabase db , String str)
	{	//	查询刚刚登录成功的用户是否已在本地列表中
		//	如果在，则返回其ID号；若不在，返回-1
		int ret = -1;
		Cursor cursor = null;
		cursor = db.query(USERS_LIST , new String[]{ID} , EMAIL + "=?", new String[]{str}, null, null, null);
		while(cursor.moveToNext())
		{
			ret = cursor.getInt(cursor.getColumnIndex(ID));
			if(ret > 0)
				return ret;
		}
		
		return -1;
	}
	
	
	
	public int GetDCount(SQLiteDatabase db , String tablename)
	{	//	得到菜品数
		int i = -1;
		String sql = "select * from " + tablename;
		Cursor cursor = db.rawQuery(sql, null);
		if(cursor != null)
			i = cursor.getCount();
		return i;
	}
	
	public void DropTabel(SQLiteDatabase db , String tablename)
	{	//	删除表
		String sql = "DROP TABLE " + tablename;
		try{
			db.execSQL(sql);
		}catch(Exception e){
			
		}
	}
	
	
	public void CreateClientTable(SQLiteDatabase db , String name) {
		
		//	检查是否有USERS_LIST表
		boolean IsNeedCreate = true;
		Cursor cursor = null;
		try{
			String sql = "select count(*) as c from sqlite_master where type = 'email' and name ='"+name.trim()+"' ";
			cursor = db.rawQuery(sql , null);
			if(cursor.moveToNext()){
				int count = cursor.getInt(0);
				if(count > 0){
					//	有指定的表
					IsNeedCreate = false;
				}
			}
		}catch(Exception e){
			
		}
		
		if(IsNeedCreate)
		{
//			String str_sql = "CREATE TABLE " + name + "(" + ID 
//			+ " INTEGER PRIMARY KEY AUTOINCREMENT , " + DISHES_NAME + " text , " + DISHES_PRICE + " real);";
//			
//			db.execSQL(str_sql);
//			System.out.println("Create \"name\" menu_table");
		}
	}

	public long AddNewUser(SQLiteDatabase db , String str_email, String str_password, boolean bRemember)
	{	//	向USERS_LIST表中添加一条记录,并返回被添加记录的ID
		int nRemember = bRemember ? 1 : 0;
		ContentValues value = new ContentValues();
		value.put(EMAIL, str_email);
		value.put(PW, str_password);
		value.put(REMEMBER_PW, nRemember);
		this.getWritableDatabase();
		long ret = db.insert(USERS_LIST, null, value);
		System.out.println("insert a record into USERS_LIST");
		return ret;		
	}

	
	public void UpdateUser(SQLiteDatabase db, int nID , String str_password , boolean bRemember)
	{	//	更新USERS_LIST中对应行的信息
		int nRemember = bRemember ? 1 : 0;
		ContentValues value = new ContentValues();
		value.put(PW , str_password);
		value.put(REMEMBER_PW , nRemember);
		db.update(USERS_LIST , value , ID + "=?" , new String[]{Integer.toString(nID)});
		System.out.println("update a record from USERS_LIST");
	}

//	public void UpdateLastLogin(SQLiteDatabase db , int nID)
//	{	//	更新LAST_LOGIN中的信息
//		ContentValues value = new ContentValues();
//		value.put(LAST_LOGIN_ID , nID);
//		db.update(LAST_LOGIN, value, ID + "=?", new String[]{"1"});
//		System.out.println("update a record from LAST_LOGIN");
//	}
	
}
