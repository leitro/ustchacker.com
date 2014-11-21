function checkform()
{
	var name=document.form.username.value;
	var patrn=/^[a-zA-Z]{1}([a-zA-Z0-9_]){5,14}$/;
	if(!patrn.exec(name))
	{
		alert('用户名只能输入6-15个以字母开头，可带数字下划线的字串');
		return false;
	}
	var mail=document.form.mail.value;
	var reg=/^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+(.[a-zA-Z0-9_-])+/;
	if(mail.length<1)
	{
		alert('邮箱不能为空');
		return false;
	}
	if(!reg.exec(mail))
	{
		alert('邮箱格式不正确，请重新输入');
		return false;
	}
	var pw=document.form.password.value;
	var pw2=document.form.password2.value;
	var patrn2=/^([a-zA-Z0-9_]){6,22}$/;
	if(!patrn2.exec(pw))
	{
		alert('密码只能输入6-22个字母、数字和下划线的字串');
		return false;
	}
	if(pw!=pw2)
	{
		alert('两次输入的密码不一致');
		return false;
	}
	return true;
}

