function ignoreSpace(string) 
{
	var temp = "";
	splitstring = string.split(" ");
	for(i = 0; i < splitstring.length; i++)
		temp += splitstring[i];
	return temp;
}
function checkform()
{
	var tag=document.form.tag.value;
	if(tag.length<1)
	{
		alert('请选择主题');
		return false;
	}
	var category=document.form.category.value;
	if(category.length<1)
	{
		alert('请选择类别');
		return false;
	}
	var title=document.form.title.value;
	if(title.length>25)
	{
		alert('标题长度不能大于25个字');
		return false;
	}
	title=ignoreSpace(title);
	if(title.length<1)
	{
		alert('请写一个标题');
		return false;
	}
	var blog=document.form.blog.value;
	blog=ignoreSpace(blog);
	if(blog.length<1)
	{
		alert('请写文章内容');
		return false;
	}
}
