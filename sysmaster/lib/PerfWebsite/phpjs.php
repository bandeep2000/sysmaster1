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
				if($username == "bandeepd" || $username == "kunalv"  ||   $username == "raymondp"  || $username == "mrugankj"  ) 
                {
					session_start();
					$_SESSION['isValid'] = true;
					$_SESSION['sess_username']  = $username;
					
					$response = array('ok' => true, 'msg' => "OK",
										'navBarData'  => getNavBar(),
										'sideBarData' => getSideBar()
										);
				}
                else {
                    $response['msg'] = "Invalid username";
                }
			}
        }
		else if($javascriptReqType == "logout")
		{
			$response = array('ok' => true, 'msg' => "OK");
			$_SESSION['isValid'] = false;
			session_destroy();
		}
        else if($javascriptReqType == "check_user_login")
		{
            $response = array('ok' => true, 'msg' => "OK");
			if($_SESSION['isValid']) {
                $response['loggedin'] = true;
            }
            else {
                 $response['loggedin'] = false;
            }
		}
        
         else if($javascriptReqType == "get_login_name")
		{
            $response = array('ok' => true, 'msg' => "OK");
            
            $response['currentUser'] = $_SESSION['sess_username'] ; 
			
		}
		else if($javascriptReqType == "get_test_beds")
		{
			$response = array('ok' => true, 'msg' => "OK");
            $response['currentUser'] = $_SESSION['sess_username'] ; 
			$response['data'] = getTestBedData();
		}
		
		else if($javascriptReqType == "get_test_results")
		{
			$response = array('ok' => true, 'msg' => "OK");
           // $response['currentUser'] = $_SESSION['sess_username'] ;
			
			$options = array();
 
			$build = $_POST['build'];
			$cardType  = $_POST['cardType'];
			$testType = $_POST['testType'];
			$osType = $_POST['osType'];

            //$response = array('ok' => false, 'msg' => "Query Failed  $build $cardType $testType $osType");
                        $response['data'] = array();
                        
                        $testTypes = array("utils","filesystems","lvm","validation","lvm-validation","diskchecker");
                        
                        $response['testTypes']= $testTypes; 
                        $response['osType']= $osType; 
                        
                        $cardTypes = array("1.1TB","2.2TB","550GB");
                        
                        foreach ($cardTypes as $cardType) {
                        
                          foreach ($testTypes as $testType) {
                            $response['data'][$cardType][$testType] = getTestResults($build,$testType,$osType,$cardType);
                        
                          }
                         }
			
		}
		
		else if($javascriptReqType == "get_perf_data")
		{
			/* TO DO
			 * Build array of performance data, and pass the arrays to perfDataOne
			$perfDataOne = array();
			$perfDataOne['blockSize'] = $_POST['blockSize1'];
			$perfDataOne['testType1'] = $_POST['blockSize1'];
			getPerfData($perfDataOne, $perfDataTwo);
			{
				$perfDataOne.blockSize;
			}
			*/
			
		    $blockSize1               = $_POST['blockSize1'];
			$testType1                = $_POST['testType1'];
			$writePercentage1         = $_POST['writePercentage1'];
			$mode1                    = $_POST['mode1'];
			$build1                   = $_POST['build1'];
			$plat_tag1                = $_POST['plat_tag1'];
			$cardType1                = $_POST['cardType1'];
			
			
			$blockSize2               = $_POST['blockSize2'];
			$testType2                = $_POST['testType2'];
			$writePercentage2         = $_POST['writePercentage2'];
			$mode2                    = $_POST['mode2'];
			$build2                   = $_POST['build2'];
			$plat_tag2                = $_POST['plat_tag2'];
			$cardType2                = $_POST['cardType2'];
			
			
			
			
		    //$response = array('ok' => false, 'msg' => "Query Failed bs $blockSize1,$writePercentage1, $testType1, $mode1,$build1, $plat_tag1,$cardType1");
			//$response = array('ok' => false, 'msg' => "Query Failed bs $table1  $cardType1  ,  $table2 $cardType2");
		    //$response = array('ok' => false, 'msg' => "Query Failed bs getPerfData($blockSize1,$testType1,$writePercentage1,$mode1,$build1,$plat_tag1,$cardType1,$blockSize2,$testType2,$writePercentage2,$mode2,$build2,$plat_tag2,$cardType2)");
			
            //$response['currentUser'] = $_SESSION['sess_username'] ; 
			
			//$resp =  getPerfData($blockSize1,$testType1,$writePercentage1,$mode1,$build1,$plat_tag1,$cardType1,$blockSize2,$testType2,$writePercentage2,$mode2,$build2,$plat_tag2,$cardType2);
			
			//$response = array('ok' => false, 'msg' => $resp);
			
			
			$response = array('ok' => true, 'msg' => "OK");
			$response['data'] = getPerfData($blockSize1,$testType1,$writePercentage1,$mode1,$build1,$plat_tag1,$cardType1,$blockSize2,$testType2,$writePercentage2,$mode2,$build2,$plat_tag2,$cardType2);
		
		}
		
		else if($javascriptReqType == "get_heat_map")
		{
			$blockSize1               = $_POST['blockSize1'];
			$testType1                = $_POST['testType1'];
			$writePercentage1         = $_POST['writePercentage1'];
			$mode1                    = $_POST['mode1'];
			$build1                   = $_POST['build1'];
			$plat_tag1                = $_POST['plat_tag1'];
			$cardType1                = $_POST['cardType1'];
			
			
			$blockSize2               = $_POST['blockSize2'];
			$testType2                = $_POST['testType2'];
			$writePercentage2         = $_POST['writePercentage2'];
			$mode2                    = $_POST['mode2'];
			$build2                   = $_POST['build2'];
			$plat_tag2                = $_POST['plat_tag2'];
			$cardType2                = $_POST['cardType2'];
			
		//$response = array('ok' => false, 'msg' => "Query Failed bs $blockSize1,$writePercentage1, $testType1, $mode1,$build1, $plat_tag1,$cardType1");
		 $response = array('ok' => true, 'msg' => "OK");
		 $response['data'] = getHeatMap($blockSize1,$testType1,$writePercentage1,$mode1,$build1,$plat_tag1,$cardType1,$blockSize2,$testType2,$writePercentage2,$mode2,$build2,$plat_tag2,$cardType2);
		 
		}
		
		
		else if($javascriptReqType == "get_ipmi_info")
		{
			$response = array('ok' => true, 'msg' => "OK");
            $response['currentUser'] = $_SESSION['sess_username'] ; 
			$response['data'] = getIPMIData();
		}
                
        else if($javascriptReqType == "get_iostat_data")
		{
			$response = array('ok' => true, 'msg' => "OK");
                        //$r = getIPMIData();
                        //$response = array('ok' => false, 'msg' => "Query Failed $r['readIOPS'] ");
            //$response['currentUser'] = $_SESSION['sess_username'] ; 
			$response['data'] = getIOStatData();
		}
		 else if($javascriptReqType == "get_iostat_read_data")
		{
			$response = array('ok' => true, 'msg' => "OK");
                        
			$response['data'] = getIOStatReadData();
		}
		
		else if($javascriptReqType == "get_term_info")
		{
			$response = array('ok' => true, 'msg' => "OK");
            $response['currentUser'] = $_SESSION['sess_username'] ; 
			$response['data'] = getTermServerData();
		}
		
		else if($javascriptReqType == "get_ipmi_term_info")
		{
			$response = array('ok' => true, 'msg' => "OK");
            $response['currentUser'] = $_SESSION['sess_username'] ; 
			$response['data'] = getIPMITermServerData();
		}
		else if($javascriptReqType == "reserve_machine")
		{
			$response = array('ok' => false, 'msg' => "User already seem to be assigned");
            $mname = $_POST['machine_name'];
            $fromUserName = $_POST['from_user'];
            
            $response['ok'] = reassignMachine($mname, $fromUserName);
            
		}
        else if($javascriptReqType == "free_machine")
		{
			$response = array('ok' => false, 'msg' => "Failed to update database with new User");
            $mname        = $_POST['machine_name'];
            $fromUserName = $_POST['from_user'];
            
            $response['ok'] = freeMachine($mname, $fromUserName);
		}
        else if($javascriptReqType == "get_power_cycle")
		{
			$rpb = $_POST['rpb'];
			$port = $_POST['port'];
            
			$response = array('ok' => true, 'msg' => "Welcome");
			$cmd = "/var/www/html/sqa/scripts/python/tests/rpb.py $rpb $port";
			
            $response['ok'] = false;
            $response['msg'] = "TO DO";
		}
		else if($javascriptReqType == "update_ipmi_info")
		{
			$response = array('ok' => false, 'msg' => "Query Failed");
			
			$mname        = $_POST['machine_name'];
			$m_ipmi       = $_POST['m_ipmi'];
			$ipmi_user_id = $_POST['ipmi_user_id'];
			$ipmi_passwd  = $_POST['ipmi_passwd'];
			
			$response['ok'] = updateIPMI($mname,$m_ipmi,$ipmi_user_id,$ipmi_passwd);
		}
		else if($javascriptReqType == "enter_machine_info")
		{
			//$response = array('ok' => false, 'msg' => "Query Failed");
			
			//machine_name="+mname+"&m_ipaddr="+mIPaddr+"&osType="+osType+"&totalMemory="+totalMemory&"totalCpus="+totalCpus&"cpuType="+cpuType
			$mname        = $_POST['machine_name'];
			$m_ipaddr     = $_POST['m_ipaddr'];
			$osType       = $_POST['osType'];
			$totalMemory  = $_POST['totalMemory'];
			$totalCpus    = $_POST['totalCpus'];
			$cpuType      = $_POST['cpuType'];
			
			$response = array('ok' => false, 'msg' => "Query Failed machine name '$mname' ip '$m_ipaddr' os '$osType' totalMemory '$totalMemory'  totalCpus '$totalCpus' cpuType '$cpuType' ");
			$response['ok'] = insertMachineInfo($mname,$m_ipaddr,$osType,$totalMemory,$totalCpus,$cpuType);   
		}
		
		else if($javascriptReqType == "enter_card_info")
		{
			
			$mname        = $_POST['machine_name'];
			$card_serial     = $_POST['card_serial'];
			$card_type       = $_POST['card_type'];
			
			
			$response = array('ok' => false, 'msg' => "Query Failed machine name '$mname' ip card_serial $card_serial card_type $card_type  ");
			
			
			$response['ok'] = insertCardInfo($card_serial,$card_type,$mname);
            
		}
		
		else if($javascriptReqType == "enter_rpb_info")
		{
			
			$rpb             = $_POST['rpb'];
			$username        = $_POST['username'];
			$password        = $_POST['password'];
			
			
			$response = array('ok' => false, 'msg' => "Query Failed $rpb, $username,$password  ");

			$response['ok'] = insertRpbInfo($rpb,$username,$password);
            
		}
		
		else if($javascriptReqType == "update_card_machine")
		{
			
			$mname        = $_POST['machine_name'];
			$card_serial     = $_POST['card_serial'];

			$response = array('ok' => false, 'msg' => "Query Failed machine name '$mname' ip card_serial $card_serial");
			
			if($_SESSION['isValid']) {
               $response['ok'] = updateCardMachine($card_serial,$mname);
            }
            else {
			
			     $response = array('ok' => false, 'msg' => "No logged in");
                 
            }

            
		}
		
		else if($javascriptReqType == "update_machine_comments")
		{
			
			$mname        = $_POST['machine_name'];
			$comment    = $_POST['comment'];
		

			$response = array('ok' => false, 'msg' => "Query Failed machine name '$mname' ip comment $comment");
			
			if($_SESSION['isValid']) {
                $response['ok'] = updateMachineComments($comment,$mname);
            }
            else {
			
			     $response = array('ok' => false, 'msg' => "No logged in");
                 
            }
  
		}
		
		//used to insert data not select, use run_select_db_query instead to select instead
		else if($javascriptReqType == "run_single_db_query")
		{
			
			$query       = $_POST['query'];
			$response = array('ok' => false, 'msg' => "Query Failed $query");
			
			
			
			if($_SESSION['isValid']) {
                          $response['ok'] =  performSingleDbQuery($query);
                          
                          
            }
            else {
			
			     $response = array('ok' => false, 'msg' => "No logged in");
                 
            }
			
		}
		
		else if($javascriptReqType == "run_select_db_query")
		{
			
			$query       = $_POST['query'];
			$response = array('ok' => false, 'msg' => "Query Failed $query");
			
			
	       $sql_query_results = performSingleDbQuery($query);
	       $result_array = array();
	
	       while ($row = mysql_fetch_assoc($sql_query_results)) 
	       {
		      array_push($result_array, $row);
	       }
	
            $response['data'] = $result_array;
			$response['ok']   = true;

			
		}
		
		else if($javascriptReqType == "get_cards")
		{
			$response = array('ok' => true, 'msg' => "OK");
            $response['currentUser'] = $_SESSION['sess_username'] ; 
			$response['data'] = getCardData();
		}
    } // isset()

    echo json_encode($response);
	exit;
?>
