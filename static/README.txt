在bootstrap-datetimepicker.min.js文件中把headTemplateV3的<span>标签全改成<i>标签

这样才能点击左和右按钮的时候是向左向右移动，而不是进去


https://github.com/smalot/bootstrap-datetimepicker/issues/126
CuGBabyBeaR,
	i found an issue with your code when click on the left right arrows, it would drill down instead of moving left or right, it was caused by the span.

	I had to remove the span from the headTemplateV3 in the js file and replace with an i tag


