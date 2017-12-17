 <?php
 // Connects to your Database
 mysql_connect("sysmaster", "root", "") or die(mysql_error());
 mysql_select_db("zperf") or die(mysql_error());

 $table="perf_data_2200";
 $bs=16384;
 $ttype="SUST8K";
 $hash1="5610e092adb9c048a0fc33ea51648b81";
 $hash2="a0a24106a87ec45bbe49ec24718ba200";
 $wpct=50;




//$SQL3 = "select test_block_size,test_jobs,test_wr_pct,test_iops from perf_data_2200 where  test_type='SUST8K' and test_block_size=4096 and test_load_type like '%Rand%' and test_mode='maxperformance' and test_tag='AMD-RHEL63' order by test_jobs;";

//$SQL4 = "select test_block_size,test_jobs,test_wr_pct,test_iops from perf_data_2200 where  test_type='PEAK' and test_block_size=4096 and test_load_type like '%Rand%' and test_mode='maxperformance' and test_tag='E5-RHEL63' order by test_jobs;";


//$data3 =  mysql_query($SQL3) or die(mysql_error());

//$data4 =  mysql_query($SQL4) or die(mysql_error());

//while($row = mysql_fetch_assoc($data3)) // loop to give you the data in an associative array so you can use it however.
//{
                    
  //  $res_by_pct1[$row['test_block_size']][$row['test_wr_pct']][$row['test_jobs']] = $row['test_iops'];
//}

//while($row = mysql_fetch_assoc($data4)) // loop to give you the data in an associative array so you can use it however.
//{
                    
  //  $res_by_pct2[$row['test_block_size']][$row['test_wr_pct']][$row['test_jobs']] = $row['test_iops'];
//}


//print_r($res_by_pct1);
//print_r($res_by_pct2);



//mysql_close();
$SQL4 = "select test_type,test_block_size,test_jobs,test_wr_pct,test_iops from perf_data_2200 where test_type in ('PEAK','SUST8K') and  test_block_size in (4096,8192,16384) and test_load_type like '%Rand%' and test_mode='maxperformance' and test_tag='AMD-RHEL63' order by test_jobs;";

$SQL3 = "select test_type,test_block_size,test_jobs,test_wr_pct,test_iops from perf_data_2200 where  test_type in ('PEAK','SUST8K') and test_block_size in (4096,8192,16384)  and test_load_type like '%Rand%' and test_mode='maxperformance' and test_tag='E5-RHEL63' order by test_jobs;";




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


print_r($res_by_pct1);
print_r($res_by_pct2);


?>
