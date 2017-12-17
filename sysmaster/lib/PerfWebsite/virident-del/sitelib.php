<?php session_start();
require_once("common.php");

function getNavBar()
{
    $barContent = '<ul class="nav">';
    $barContent .= '<li><a href="index.php"><b>Home</b></a></li>';

    if(isUserLoggedIn())
    {
		$barContent .= '<li><a href="#" onclick="javascript: performLogout()"><b>Logout</b></a></li>';
	}
    $barContent .= '</ul>';

    return $barContent;
}

function getSideBar()
{
    if(!isUserLoggedIn())
    {
		$barContent = '<h2>Wise Words</h2>';
		$barContent .= '<p>&quot;Great works are performed not by strength,';
		$barContent .= 'but by perseverance.&quot; </p>';

		$barContent .= '<p class="align-right">- Samuel Johnson</p>';
    }
    else
    {
		$barContent .= '<ul class="nav nav-list">';
		$barContent .= 		'<li class="nav-header"><font color="black">My World</font></li>';
		$barContent .= 		'<li> <A HREF="#"  onClick="javascript: alert("hello!")">&nbsp;<i class="icon-home"></i>Sample Menu</a> </li>';
		$barContent .= '</ul><HR>';
    }

    return $barContent;
}

?>
