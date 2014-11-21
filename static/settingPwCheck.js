function checkform()
{
	var pw=document.form.newpw.value;
	var pw2=document.form.newpw2.value;
	if(pw.length<6)
	{
		alert('密码长度不能小于6位');
		return false;
	}
	if(pw!=pw2)
	{
		alert('两次输入的密码不一致');
		return false;
	}
}

