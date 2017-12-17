<?php session_start();
require_once("common.php");

function getNavBar()
{
    $barContent = '<ul class="nav">';
    $barContent .= '<li><a href="index.php"><b>Home</b></a></li>';
	//$barContent .= '<li><a href="#" onclick="plotGraph1()"><b>plotGraph</b></a></li>';
	//$barContent .= '<li><a href="#" onclick="loadIPMITermServerPage()"><b>Machines-Info</b></a></li>';
	//$barContent .= '<li><a href="#" onclick="loadPerformancePage() "><b>Perf-Results</b></a></li>';
	//$barContent .= '<li><a href="#" onclick="loadHeatMapPage()"><b>Heat-Map</b></a></li>';
	//$barContent .= '<li><a href="#" onclick="loadAllCards()"><b>Cards-info</b></a></li>';
	//$barContent .= '<li><a href="#" onclick="loadIPMIPage()"><b>IPMI-info</b></a></li>';
	$barContent .= '<li><a href="#" onclick="loadRpbPage()"><b>Rpb-Host-info</b></a></li>';
	//$barContent .= '<li><a href="#" onclick="loadTermServerPage() "><b>TermSrv-info</b></a></li>';
	//$barContent .= '<li><a href="#" onclick="loadUpdateIPMIPage() "><b>UpdateIPMI-info</b></a></li>';
	$barContent .= '<li><a href="#" onclick="insertMachinePage() "><b>Enter-New-Machine</b></a></li>';
	$barContent .= '<li><a href="#" onclick="insertRpbPage() "><b>Enter-New-Rpb</b></a></li>';
	//$barContent .= '<li><a href="#" onclick="insertCardPage() "><b>Enter-New-Card</b></a></li>';
	//$barContent .= '<li><a href="#" onclick="loadPerformancePage() "><b>Perf-Results</b></a></li>';
	//$barContent .= '<li><a href="#" onclick="loadTestResultsPage() "><b>Test-Results</b></a></li>';
	//$barContent .= '<li><a href="#" onclick=" loadBuildTestResultsPage() "><b>Test-Results</b></a></li>';
	
//$barContent .= '<li class="dropdown">
 //                       <a href="#" class="dropdown-toggle" data-toggle="dropdown">Dropdown <b class="caret"></b></a>
 //                       <ul class="dropdown-menu">
 //                         <li><a href="#">Action</a></li>
 //                         <li><a href="#">Another action</a></li>
  //                        <li><a href="#">Something else here</a></li>
 //                         <li class="divider"></li>
//                          <li><a href="#">Separated link</a></li>
 //                       </ul>
 //                     </li>';

	//$barContent .= '<li><a href="#"><b>Rpb-Power-Cycle</b></a>';
	//$barContent .= '<ul>';
	
	 //$barContent .= '<li><a href="#" onclick="loadPowerCyclePage()"><b>Rpb-Power-Cycle</b></a></li>';
	
	//$barContent .= '</ul >';
	//$barContent .= '</li>';
	

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
		$barContent = '<h2>You are logged in!</h2>';
        $barContent .= '<p>You are logged in as: <b>' . $_SESSION['sess_username'] . '</b></p>';
        
        $barContent .= '<div id=\'currentUsername\' value=' . $_SESSION['sess_username'] .'></div>';
    }

    return $barContent;
}

function getTestBedData()
{
	$sql_query_results = performSingleDbQuery("SELECT * FROM tb");
	$result_array = array();
	
	while ($row = mysql_fetch_assoc($sql_query_results)) 
	{
		if($row[user] == "" || $row[user] == null) {
			$row[user] = "FREE";
		}
		
		$user_card_results = performSingleDbQuery("SELECT * FROM cards WHERE tb_name='" . $row[tb_name] . "'");
		while ($rows = mysql_fetch_assoc($user_card_results)) {
			$row[card_details] .= $rows[cardDescription] . "&nbsp;" . $rows[serial] . "<BR/>";
		}
		if($row[card_details] == "" || $row[card_details] == null) {
			$row[card_details] = "None";
		}
		
		array_push($result_array, $row);
	}
	//$currentUser = $_SESSION['sess_username'];
    
	//return $result_array;
    
    //$result_array1 = array('currentUser' => $currentUser,'result_array' => $result_array);
    return $result_array;
}


function getTestResults($build,$testType,$osType,$cardType)
{

    //select * from testResults where build like '%49400.C5%' and osVersion="redhat6" and cardType="550GB" and testcaseStr="lvm";
	$sql_query_results = performSingleDbQuery("select * from testResults where build like '%$build%' and osVersion='$osType' and cardType='$cardType' and testcaseStr='$testType'");
	$result_array = array();
	
	while ($row = mysql_fetch_assoc($sql_query_results)) 
	{

		array_push($result_array, $row);
	}
	
    return $result_array;
}

function getCardData()
{
	$sql_query_results = performSingleDbQuery("select serial,cardDescription,tb.tb_name,tb.user from tb,cards where tb.tb_name=cards.tb_name");
	$result_array = array();
	
	while ($row = mysql_fetch_assoc($sql_query_results)) 
	{
		
		
		array_push($result_array, $row);
	}
	
    return $result_array;
}

function getIPMIData()
{
	$sql_query_results = performSingleDbQuery("SELECT tb_name,ipmi_addr,ipmi_userid,ipmi_passwd from tb;");
	$result_array = array();
	
	while ($row = mysql_fetch_assoc($sql_query_results)) 
	{
		array_push($result_array, $row);
	}
	
    return $result_array;
}

//gets ipmi,rpb and term server data
function getIPMITermServerData()
{
	$sql_query_results = performSingleDbQuery("SELECT tb_name,ipmi_addr,ipmi_userid,ipmi_passwd,rpb,rpbPort,termServer,termPort from tb;");
	$result_array = array();
	
	while ($row = mysql_fetch_assoc($sql_query_results)) 
	{
		array_push($result_array, $row);
	}
	
    return $result_array;
}

function getPerfData($blockSize1,$testType1,$writePercentage1,$mode1,$build1,$plat_tag1,$cardType1,$blockSize2,$testType2,$writePercentage2,$mode2,$build2,$plat_tag2,$cardType2)

{

// Connects to your Database
 mysql_connect("sysmaster", "root", "") or die(mysql_error());
 mysql_select_db("zperf") or die(mysql_error());

$table1="perf_data_550";
if ($cardType1 =="2200") {
   $table1="perf_data_2200";
 
 }
 
 $table2 ="perf_data_550";
if ($cardType2 == "2200") {
   $table2 = "perf_data_2200";
 
 }

# Use Blocksize 8192,4096,16384 

//$bs=16384;

//$bs=$blockSize;
//$ttype=$testType;
//$wpct=$writePercentage;

# Use SUST8K or PEAK
 //$ttype="SUST8K";
 $hash1="5610e092adb9c048a0fc33ea51648b81";
 $hash2="a0a24106a87ec45bbe49ec24718ba200";
 
# Use any from  0,10,25,50,75,90,100 as value
//$wpct=50;

//$SQL1 = "select test_jobs,test_wr_pct,test_bw,test_iops,test_read_lat+test_write_lat as lat_sum,test_tag from $table where test_block_size=$bs and test_reshash='$hash1'  and test_type='$ttype' and test_wr_pct='$wpct' order by test_jobs";

//$SQL2 = "select test_jobs,test_wr_pct,test_bw,test_iops,test_read_lat+test_write_lat as lat_sum,test_tag from $table where test_block_size=$bs and test_reshash='$hash2' and test_type='$ttype'  and test_wr_pct='$wpct' order by test_jobs";

///select test_jobs,test_wr_pct,test_bw,test_iops,test_read_lat+test_write_lat as lat_sum,test_tag from perf_data_2200 where 
//test_block_size='4096' and test_type='PEAK' and test_wr_pct='0'  and test_mode="maxperformance" and test_build="48316.C5"  and test_tag="EP-FAST-SLESSP2"  order by test_jobs;

$SQL1 = "select test_jobs,test_wr_pct,test_bw,test_iops,test_read_lat+test_write_lat as lat_sum,test_tag from $table1 where test_block_size='$blockSize1' and test_load_type like '%Rand%' and test_type='$testType1' and test_wr_pct='$writePercentage1'  and test_mode='$mode1' and test_build='$build1'  and test_tag='$plat_tag1'  order by test_jobs";
$SQL2 = "select test_jobs,test_wr_pct,test_bw,test_iops,test_read_lat+test_write_lat as lat_sum,test_tag from $table2 where test_block_size='$blockSize2' and test_load_type like '%Rand%' and test_type='$testType2' and test_wr_pct='$writePercentage2'  and test_mode='$mode2' and test_build='$build2'  and test_tag='$plat_tag2'  order by test_jobs";

$result_array1 = array();
$result_array2 = array();


 $data1 = mysql_query($SQL1) or die(mysql_error());

 while($info = mysql_fetch_array( $data1 ))
 {
 
 array_push($result_array1, $info);
 
 }

 $data2 = mysql_query($SQL2) or die(mysql_error());

 while($info = mysql_fetch_array( $data2 ))
 {
 
 array_push($result_array2, $info);
 

 }
  $response = array('data1' => $result_array1 , 'data2' => $result_array2);

  //$response1 = array('data1' => $SQL1, 'data2' => $SQL2);
 return $response;

mysql_close();

}
function getHeatMap($blockSize1,$testType1,$writePercentage1,$mode1,$build1,$plat_tag1,$cardType1,$blockSize2,$testType2,$writePercentage2,$mode2,$build2,$plat_tag2,$cardType2) {

mysql_connect("sysmaster", "root", "") or die(mysql_error());
 mysql_select_db("zperf") or die(mysql_error());
 
 $table1="perf_data_550";
if ($cardType1 =="2200") {
   $table1="perf_data_2200";
 
 }
 
 $table2 ="perf_data_550";
if ($cardType2 == "2200") {
   $table2 = "perf_data_2200";
 
 }

 $table="perf_data_2200";
 $bs=16384;
 $ttype="SUST8K";
 $hash1="5610e092adb9c048a0fc33ea51648b81";
 $hash2="a0a24106a87ec45bbe49ec24718ba200";
 $wpct=50;

$SQL4 = "select test_type,test_block_size,test_jobs,test_wr_pct,test_iops from $table1 where test_type in ('PEAK','SUST8K') and  test_block_size in (4096,8192,16384) and test_load_type like '%Rand%' and test_mode='maxperformance' and test_tag='E5-RHEL63-IODRIVE' order by test_jobs;";

$SQL3 = "select test_type,test_block_size,test_jobs,test_wr_pct,test_iops from $table2 where  test_type in ('PEAK','SUST8K') and test_block_size in (4096,8192,16384)  and test_load_type like '%Rand%' and test_mode='maxperformance' and test_tag='E5-RHEL63' order by test_jobs;";

$SQL4 = "select test_type,test_block_size,test_jobs,test_wr_pct,test_iops from $table1 where test_type in ('PEAK','SUST8K') and  test_block_size in (4096,8192,16384) and test_load_type like '%Rand%' and test_mode='$mode1' and test_tag='$plat_tag1' order by test_jobs;";

$SQL3 = "select test_type,test_block_size,test_jobs,test_wr_pct,test_iops from $table2 where  test_type in ('PEAK','SUST8K') and test_block_size in (4096,8192,16384)  and test_load_type like '%Rand%' and test_mode='$mode2' and test_tag='$plat_tag1' order by test_jobs;";





$data3 =  mysql_query($SQL3) or die(mysql_error());

$data4 =  mysql_query($SQL4) or die(mysql_error());

while($row = mysql_fetch_assoc($data3)) // loop to give you the data in an associative array so you can use it however.
{

    $res_by_pct1[$row['test_type']][$row['test_block_size']][$row['test_wr_pct']][$row['test_jobs']] = $row['test_iops'];
}

while($row = mysql_fetch_assoc($data4)) // loop to give you the data in an associative array so you can use it however.
{

    $res_by_pct2[$row['test_type']][$row['test_block_size']][$row['test_wr_pct']][$row['test_jobs']] = $row['test_iops'];
}





  $response = array('data1' => $res_by_pct1 , 'data2' => $res_by_pct2);

 
 return $response;


mysql_close();


}
		
function getTermServerData()
{
	$sql_query_results = performSingleDbQuery("SELECT tb_name,termServer,termPort from tb;");
	$result_array = array();
	
	while ($row = mysql_fetch_assoc($sql_query_results)) 
	{
		array_push($result_array, $row);
	}
	
    return $result_array;
}

function getIOStatData()
{
        $machine = "172.16.65.48";
	$sql_query_results = performSingleDbQuery("select * from iostat where machineName=\"$machine\" order by collumn_1 desc limit 1000;");
	$result_array = array();
	
	while ($row = mysql_fetch_assoc($sql_query_results)) 
	{
		array_push($result_array, $row);
	}
	
    return $result_array;
}


function reassignMachine($mname,$fromUser)
{
    $newUser = $_SESSION['sess_username'];
    
    if ( $newUser == $fromUser) {
       return false;
    
    }

    // TODO 
    $query = "update tb set user = \"$newUser\" where tb_name = \"$mname\"";
    performSingleDbQuery($query);
    
    $subject = "Testbed Assignment: $mname reassigned to $newUser from $fromUser";
    $message = $subject;
    
    sendEmail($newUser,$subject,$message);
    
    // if user name is free, dont send the mail to free users
    if ( $fromUser == "FREE") {
        return true;
    }
    sendEmail($fromUser,$subject,$message);
    
    return true;
}
function updateIPMI($mname,$m_ipmi,$ipmi_user_id,$ipmi_passwd)
{
    $newUser = $_SESSION['sess_username'];
    //update tb set ipmi_addr="172.16.64.56",ipmi_userid="ADMIN",ipmi_passwd="ADMIN" where tb_name="sqa11";
    $query = "update tb set ipmi_addr=\"$m_ipmi\",ipmi_userid=\"$ipmi_user_id\",ipmi_passwd=\"$ipmi_passwd\" where tb_name = \"$mname\"";
    return performSingleDbQuery($query);
    
    
    
}

function updateCardMachine($card_serial,$mname)
{
    $newUser = $_SESSION['sess_username'];
    //update tb set ipmi_addr="172.16.64.56",ipmi_userid="ADMIN",ipmi_passwd="ADMIN" where tb_name="sqa11";
	// update cards set tb_name="sqa05" where serial="test";
    $query = "update cards set tb_name=\"$mname\" where serial=\"$card_serial\"";
    return performSingleDbQuery($query);
}


function updateMachineComments($comment,$mname)
{
    $newUser = $_SESSION['sess_username'];
    //update tb set ipmi_addr="172.16.64.56",ipmi_userid="ADMIN",ipmi_passwd="ADMIN" where tb_name="sqa11";
	// update cards set tb_name="sqa05" where serial="test";
    $query = "update tb set comment=\"$comment\" where tb_name=\"$mname\"";
    return performSingleDbQuery($query);
}

function insertMachineInfo($mname,$m_ipaddr,$osType,$totalMemory,$totalCpus,$cpuType) {
   $newUser = $_SESSION['sess_username'];
    //update tb set ipmi_addr="172.16.64.56",ipmi_userid="ADMIN",ipmi_passwd="ADMIN" where tb_name="sqa11";
    //$query = "update tb set ipmi_addr=\"$m_ipmi\",ipmi_userid=\"$ipmi_user_id\",ipmi_passwd=\"$ipmi_passwd\" where tb_name = \"$mname\"";
	$query = "insert into tb (tb_name,ip_addr,osType,totalMemory,cpus,cpuType) values (\"$mname\",\"$m_ipaddr\",\"$osType\",\"$totalMemory\",\"$totalCpus\",\"$cpuType\")";
    return performSingleDbQuery($query);

}

function insertCardInfo($card_serial,$card_type,$mname) {
   $newUser = $_SESSION['sess_username'];
    //update tb set ipmi_addr="172.16.64.56",ipmi_userid="ADMIN",ipmi_passwd="ADMIN" where tb_name="sqa11";
    //$query = "update tb set ipmi_addr=\"$m_ipmi\",ipmi_userid=\"$ipmi_user_id\",ipmi_passwd=\"$ipmi_passwd\" where tb_name = \"$mname\"";
	$query = "insert into cards  values (\"$card_serial\",\"$card_type\",\"$mname\")";
    return performSingleDbQuery($query);

}

function insertRpbInfo($rbp,$username,$password) {
    $newUser = $_SESSION['sess_username'];
    
	$query = "insert into Rpb  values (\"$rpb\",\"$username\",\"$password\")";
	//$query = "insert into Rpb  values (\"$rpb\",\"$username\",\"$password\")";
    return performSingleDbQuery($query);

}



function freeMachine($mname,$fromUser)
{
    $newUser = $_SESSION['sess_username'];

    $query = "update tb set user = \"\" where tb_name = \"$mname\"";
    $queryResult = performSingleDbQuery($query);
    
    
    $subject = "Testbed Assignment: $mname released by $newUser";
    sendEmail($newUser,$subject,$message);
    return true;
}


?>
