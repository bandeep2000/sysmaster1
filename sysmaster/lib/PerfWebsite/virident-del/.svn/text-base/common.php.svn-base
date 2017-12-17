<?php session_start();

function SQLE($s)
{
	return mysql_real_escape_string($s);
	return $s;
}

function escapeString($s)
{
	return str_replace("'", "\'", $s);
}

function unescapeString($s)
{
	return str_replace("\'", "'", $s);
}


function isUserLoggedIn()
{
  return (isset($_SESSION) && isset($_SESSION['isValid']) && $_SESSION['isValid']);
}

function getSessionUsername()
{
	if(isUserLoggedIn()) {
		return $_SESSION['sess_username'];
	}
	else {
		return "@invalid_u5er!";
	}
}
// Opens the Database Table using the SQL Database Credentials
function openDatabase()
{
	$db_user = "root";
	$password = "";
	$database = "virident_db";
	$link = mysql_connect("localhost", $db_user, $password);
	if(!link)
		die("Unable to connect to database");
	@mysql_select_db($database) or die( "Unable to select database");
	return $link;
}

function closeDatabase()
{
	mysql_close();
}

function performSingleDbQuery($query)
{
	//TODO remove the open/close db part. but argue with preet first.
	openDatabase();
	$results = mysql_query($query);
	closeDatabase();
	
	return $results;
}

//TODO remove. this is redundant.
function performSingleDbQueryGetResults($query)
{
	return performSingleDbQuery($query);
}
function performSingleDbQueryGetRow($query)
{
	return mysql_fetch_assoc(performSingleDbQuery($query));
}

function getResultAssoc($sqlResult)
{
	return mysql_fetch_assoc($sqlResult);
}

// Performs Query and returns the #rows returned from the Query
function getQueryCount($query)
{
	$results = mysql_query($query);
	$count   = null==$results ? 0 : mysql_num_rows($results);
	return $count;
}

//returns # of rows based on results;
function getResultCount($result)
{
	return mysql_num_rows($result);
}

// Get Single Quoted & Escaped SQL string
function sqlQStr($s)
{
	return "'" . SQLE($s) . "'";
}

// Damn single quoted strings for SQL gets your eyes tired!
function sqlArgs1($A1)
{
	return "('" . SQLE($A1) . "')";
}

function sqlArgs2($A1, $A2)
{
	return "('" . SQLE(A1) . "', '" . SQLE($A2) . "')";
}

function sqlArgs3($A1, $A2, $A3)
{
	return "('" . SQLE($A1) . "', '" . SQLE($A2) . "', '" . SQLE($A3) . "')";
}

?>