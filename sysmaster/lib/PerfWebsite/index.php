<?php session_start();
require_once("sitelib.php");
?>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
	<meta name="Description" content="Virident" />
	<meta name="Keywords" content="Virident" />
	<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
	<meta name="Distribution" content="Global" />
	<meta name="author" content="Bandeep" />
	<meta name="Robots" content="index,follow" />
	<title>Virident SQA page</title>
	<link rel="shortcut icon" type="image/x-icon" href="images/favicon.ico">

	<!-- Include JQuery File (1.7.1)  -->                                                                                 
	<script type="text/javascript" src="jquery.min.js"></script>
	
	<!-- <script type="text/javascript" src="http://jzaefferer.github.com/jquery-validation/jquery.validate.js"></script> -->
	
	<!-- Kunal Charts -->
    <script src="js/jquery.min.js" type="text/javascript"></script>
   <script src="js/highcharts.js" type="text/javascript"></script>
   <script src="js/script.js" type="text/javascript"></script>
   <script type="text/javascript" src="js/jquery.graphup.pack.js"></script>
	<!-- Virident JS & CSS -->
	<script type="text/javascript" src="jsphp.js"></script>  
	<script type="text/javascript" src="tfilter.js"></script>  
	<script type="text/javascript" src="jquery.jeditable.js"></script>  
	<style>
		.highlighted { background: yellow; }
	</style>
 <style>

body { font:14px Helvetica,Arial,sans-serif; }
	p { max-width:40em; }
	table { margin:2em 0; }
	th, td { padding:0.4em; width:6em; text-align:center; }
	th { border:1px solid #ccc; border-width:0 1px 1px 0; }

	/* Special styles for the demo tables */
	#ktable1 .top50 { font-weight:bold; text-shadow:0 1px 0 rgba(255,255,255,0.25); }
	#ktable2 td:hover span { opacity:1 !important; font-weight:bold; cursor:default; }
 </style>

	
	<!-- Bootstrap -->
	<script src="bootstrap/js/bootstrap.min.js"></script>
	<link rel="stylesheet" href="bootstrap/css/bootstrap.css" type="text/css" />
</head>
<body>

<div class="navbar">
	<div class="navbar-inner">
		<div class="container" style="width: auto;">
			<a class="brand" href="#">Virident</a>

			<!--
			<form class="navbar-search" action="">
				<input id="quickfind" name="quickfind" type="text" class="search-query span3" placeholder="Filter">
			</form>
			-->

			<div id="TopBarSiteDiv">
				<?php echo getNavBar(); ?>
				<ul class="nav pull-right"><li class="divider-vertical"></li></ul>

				<form class="navbar-search" onSubmit="return false;">
					<input id="quickfind" name="quickfind" type="text" class="search-query span3" placeholder="Filter">
				</form>
				
				
				<?php if(!isUserLoggedIn()) { ?>
					<!--
					<form class="navbar-form pull-right" onSubmit="return false;">
						<button class="btn btn-primary" onClick="javascript: showRegistrationModal()"/><i class="icon-user icon-white"></i>&nbsp;<b>Sign Up!</b></button>
					</form>
					<ul class="nav pull-right"><li class="divider-vertical"></li></ul>
					-->
					
					<form class="navbar-form pull-right" onSubmit="return false;">
						<input type="text"     name="loginUsername" id="loginUsername" class="input-small" placeholder="e.g travisv" >
						<!--<input type="password" name="password"      id="password"      class="input-small" placeholder="Password">-->
						&nbsp;&nbsp;<button  class="btn btn-success" type="submit" onclick="attempt_login()"><i class="icon-share-alt icon-white"></i><b>Sign in</b></button>
					</form>

					<?php } ?>
				</div> <!-- TopBarDiv -->
			</div> <!-- /container -->
		</div><!-- /navbar-inner -->
	</div><!-- /navbar -->

	<div class="container-fluid">
		<div class="content">
			<div class="row"> 
				<div class="span3">
					<div class="sidebar">
						<div class="alert alert-info">
							<div id="sideBarSiteDiv">
								<?php echo getSideBar(); ?>
							</div>
						</div>
					</div>
				</div>
				<div class="span8">
					<div id="popupModalDiv"></div>				<!-- Modal used for dialog boxes or alert messages -->
					<div id="mainContentSiteDivTopMsg"></div>	<!-- Semi permanent message appended before main content area of the page -->
					<div id="mainContentSiteDiv">				<!-- Main content area for the user -->
						<h2><a href="#">Welcome</a></h2>
					</div>
				</div>
			</div> <!-- row -->
		</div>
	</div>

</body>
</html>
