<?php session_start();
require_once("sitelib.php");

    // Default response
    $response = array('ok' => false, 'msg' => "Invalid Javascript Request");
  
    $javascriptReqType = $_POST['action'];
    if(isset($javascriptReqType))
    {
        if($javascriptReqType == "login" || $javascriptReqType == "newRegistration")
        {
			$username = $_POST['username'];
			$password = $_POST['password'];
			
			if($javascriptReqType == "newRegistration") 
			{
				
			}
			
			if($javascriptReqType == "login")
			{
				if(false) {
				}
				else
				{
					session_start();
					$_SESSION['isValid'] = true;
					$_SESSION['sess_username']  = $username;
					
					$response = array('ok' => true, 'msg' => "OK",
										'navBarData'  => getNavBar(),
										'sideBarData' => getSideBar()
										);
				}
			}
        }
		else if($javascriptReqType == "logout")
		{
			$response = array('ok' => true, 'msg' => "OK");
			$_SESSION['isValid'] = false;
			session_destroy();
		}

    } // isset()

    echo json_encode($response);
	exit;
?>

