package push800.photograph.menu;

public class MenuInfo {
	/**
	 * 标题
	 */
	public String title;
	public int imgsrc;
	/**
	 * 是否隐藏
	 */
	public boolean ishide;
	/**
	 * menuId
	 */
	public int menuId;
	public MenuInfo(int menuId, String title,int imgsrc,Boolean ishide){
		this.menuId=menuId;
		this.title=title;
		this.imgsrc=imgsrc;
		this.ishide=ishide;
	}
}
