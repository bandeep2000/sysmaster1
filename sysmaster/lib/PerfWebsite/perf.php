 <?php
 // Connects to your Database
 mysql_connect("sysmaster", "root", "") or die(mysql_error());
 mysql_select_db("zperf") or die(mysql_error());

 $table="perf_data_2200";

# Use Blocksize 8192,4096,16384 

$bs=16384;

# Use SUST8K or PEAK
 $ttype="SUST8K";
 $hash1="5610e092adb9c048a0fc33ea51648b81";
 $hash2="a0a24106a87ec45bbe49ec24718ba200";
 
# Use any from  0,10,25,50,75,90,100 as value
$wpct=50;

$SQL1 = "select test_jobs,test_wr_pct,test_bw,test_iops,test_read_lat+test_write_lat as lat_sum,test_tag from $table where test_block_size=$bs and test_reshash='$hash1'  and test_type='$ttype' and test_wr_pct='$wpct' order by test_jobs";

$SQL2 = "select test_jobs,test_wr_pct,test_bw,test_iops,test_read_lat+test_write_lat as lat_sum,test_tag from $table where test_block_size=$bs and test_reshash='$hash2' and test_type='$ttype'  and test_wr_pct='$wpct' order by test_jobs";


 $data1 = mysql_query($SQL1) or die(mysql_error());

 while($info = mysql_fetch_array( $data1 ))
 {
 $cat1[] = $info['test_jobs'];
 $iops1[]=$info['test_iops'];
 $mbps1[]= $info['test_bw'];
 $lat1[] = $info['lat_sum'];
 $tag1[] =  $info['test_tag'];
 }

 $data2 = mysql_query($SQL2) or die(mysql_error());

 while($info = mysql_fetch_array( $data2 ))
 {
 $cat2[] = $info['test_jobs'];
 $iops2[]=$info['test_iops'];
 $mbps2[]= $info['test_bw'];
 $lat2[] = $info['lat_sum'];
 $tag2[] =  $info['test_tag'];

 }

$h1=$tag1[1];
$h2=$tag2[1];

echo "Comparing $h1 vs $h2 for $bs - $wpct - $ttype";



mysql_close();


?>
<html>
<head>
<title>Virident  FlashMax II SQA Performance Charts </title>

<link rel="stylesheet" href="css/style.css" type="text/css" />
<link rel="stylesheet" href="css/style1.css" type="text/css" />
<script src="js/jquery.min.js" type="text/javascript"></script>
<script src="js/exporting.js" type="text/javascript"></script>
<script src="js/highcharts.js" type="text/javascript"></script>
<script src="js/script.js" type="text/javascript"></script>
<script type="text/javascript">
$(function(){
var viewid = "container1";
var chart = new Highcharts.Chart({
  chart: {
     renderTo: 'container1',
     zoomType: 'xy'
  },
  title: {
     text: 'Bandwidth IOPS and Latency for <?php echo  "for bs=$bs , Write%=$wpct , Test=$ttype" ?> '
  },
  subtitle: {
     text: 'Source: Systems QA Performance DATA'
  },
  xAxis: [{
     labels: {
        formatter: function() {
           return this.value+' Thread';
        },
        style: {
           color: '#4572A7'
        }
     },

     categories: [<?php echo join($cat1, ",") ?> ]
  }],
  yAxis: [{ // Primary yAxis
     labels: {
        formatter: function() {
           return this.value+' IOPS';
        },
        style: {
           color: '#4572A7'
        }
     },
     title: {
        text: 'IOPS',
        style: {
           color: '#4572A7'
        }
     },
     opposite: true

  }, { // Secondary yAxis
     gridLineWidth: 0,
     title: {
        text: 'Latency',
        style: {
           color: '#4572A7'
        }
     },
     labels: {
        formatter: function() {
           return this.value+' µs';
        },
        style: {
           color: '#4572A7'
        }
     }

  }, { // Tertiary yAxis
     gridLineWidth: 0,
     title: {
        text: 'Bandwidth',
        style: {
           color: '#4572A7'
        }
     },
     labels: {
        formatter: function() {
            return this.value+' MB/s';
        },
        style: {
           color: '#4572A7'
        }
     },
     opposite: true
  }],

  tooltip: {
                formatter: function() {
                    var unit = {
                        'IOPS <?php echo $h1; ?>': ' IOPS',
                        'Latency <?php echo $h1; ?>': ' µs',
                        'Bandwidth <?php echo $h1; ?>': ' MB/s',
                        'IOPS <?php echo $h2; ?>': ' IOPS',
                        'Latency <?php echo $h2; ?>': ' µs',
                        'Bandwidth <?php echo $h2; ?>': ' MB/s'

                    }[this.series.name];
    
                    return ''+
                        this.x +': '+ this.y +' '+unit;
                }
            },
  legend: {
     layout: 'vertical',
     align: 'left',
     x: 120,
     verticalAlign: 'top',
     y: 80,
     floating: true,
     backgroundColor: '#FFFFFF'
  },
  series: [{
     name: 'Latency <?php echo $h1; ?>',
     color: '#89A54E',
     type: 'column',
     yAxis: 1,
     data: [ <?php echo join($lat1, ",") ?> ]
      

  },
 {
     name: 'Latency <?php echo $h2; ?>',
     color: '#AA4643',
     type: 'column',
     yAxis: 1,
     data: [<?php echo join($lat2, ",") ?>]
 

  }, 

    {
     name: 'Bandwidth <?php echo $h1; ?>',
     type: 'spline',
     color: '#89A54E',
     yAxis: 2,
     data: [<?php echo join($mbps1, ",") ?>  ],
     marker: {
        enabled: false
     },
     dashStyle: 'shortdot'

  },{
     name: 'Bandwidth <?php echo $h2; ?>',
     type: 'spline',
     color: '#AA4643',
     yAxis: 2,
     data: [<?php echo join($mbps2, ",") ?> ],
     marker: {
        enabled: false
     },
     dashStyle: 'shortdot'

  }, 

  {
     name: 'IOPS <?php echo $h1; ?>',
     color: '#89A54E',
     type: 'spline',
     data: [<?php echo join($iops1, ",") ?> ] 
  },
{
     name: 'IOPS <?php echo $h2; ?>',
     color: '#AA4643',
     type: 'spline',
     data: [<?php echo join($iops2, ",") ?>]
  }

]
});
});
</script>
</head>
<body>

<div id='container1' ></div>

</body>
</html>
