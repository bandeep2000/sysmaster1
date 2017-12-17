// ***************************************************/
// Encodes URL to transmit + and spaces
// ***************************************************/
function urlencode(str) {return encodeURI(str); }
function urldecode(str) {return decodeURI(str); }
function isValidRegExStr(str, regExStr) { return regExStr.test(str); }

function isValidWholeNumber(str)
{
	var regex = /^\s*\d+\s*$/;
	return regex.test(str);
}
function isValidEmail(str)
{
  var regex = /^[-_.a-z0-9]+@(([-_a-z0-9]+\.)+(ad|ae|aero|af|ag|ai|al|am|an|ao|aq|ar|arpa|as|at|au|aw|az|ba|bb|bd|be|bf|bg|bh|bi|biz|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|com|coop|cr|cs|cu|cv|cx|cy|cz|de|dj|dk|dm|do|dz|ec|edu|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gh|gi|gl|gm|gn|gov|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|in|info|int|io|iq|ir|is|it|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|mg|mh|mil|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|museum|mv|mw|mx|my|mz|na|name|nc|ne|net|nf|ng|ni|nl|no|np|nr|nt|nu|nz|om|org|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|pro|ps|pt|pw|py|qa|re|ro|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|sk|sl|sm|sn|so|sr|st|su|sv|sy|sz|tc|td|tf|tg|th|tj|tk|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|um|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)|(([0-9][0-9]?|[0-1][0-9][0-9]|[2][0-4][0-9]|[2][5][0-5])\.){3}([0-9][0-9]?|[0-1][0-9][0-9]|[2][0-4][0-9]|[2][5][0-5]))$/i;
  return regex.test(str);
}
function isValidName(str)
{
	var regex = /^[^ ][a-zA-Z ]+$/;
	return regex.test(str);
}
function getTableColumn(content)
{
	return '<td>' + content + '</td>';
}

// *** Is executed once the webpage is fully loaded.
$(window).load(function () 
{
	loadAllTestBeds();
});

// *** When document is ready
$(document).ready(function ()
{

});

/**
 * This updates the Webpage's side-bar given HTML content
 */
function updateSideBar(theContent)
{
	$("#sideBarSiteDiv").html(theContent);
}

/**
 * This modifies the temporary HTML DIV used to output Error Messages or Temporary notificaitons to the user
 */
function prependMainContent(theContent, timeout)
{
	//TODO when multiple calls are made, dismissible alert doesn't display for full 5 seconds
	var topDiv = $("#mainContentSiteDivTopMsg");
	topDiv.html(theContent).show();
	if(timeout) {
		setTimeout(function () {
			// TODO: test this function when multiple alerts are displayed
			//topDiv.fadeOut(500);
		}, timeout);
	}
}

/**
 * This updates the webpage's main content area
 */
function updateMainContent(theContent)
{
	$("#mainContentSiteDiv").html(theContent);
	prependMainContent('');
}
// This updates the Top Navigation Webpage Area
function updateTopBar(theContent)
{
	$("#TopBarSiteDiv").html(theContent);
}

// Gets a dismissable alert message to the user given its title, message, and alertType, which could be "info", "warning", or "error"
function getDismissibleAlert(title, msg, alertType)
{
	var alert = '<div class="alert alert-block alert-' + alertType + ' fade in">';
		alert += '<a class="close" data-dismiss="alert" href="#">&times;</a>';
		alert += '<strong>' + title + '</strong></BR>' + msg;
		alert += '</div>';
		
	return alert;
}

// Gets a wrapped text inside an "alert-info" div of Bootstrap CSS
function getWrappedText(text)
{
	var content = '<div class="alert alert-info">';
		content += text;
		content += '</div>';
		
	return content;
}

// This shows a splash screen
// display: If true, displays the splash screen, otherwise hides it
// message: Optional parameter of message, if null, "Loading . . ." message is displayed
function displayLoadingSplashScreen(display, message)
{
	(display) ? showPopupModal(message ? message : "Loading", "", "", "150") : hidePopupModal();
}

// Sends Ajax request
// action: The action to send to phpjs.php web-page
// postVars: The post variables to send to phpjs.php
// funcAfterSuccess, the function to execute after successful ajax response
//						This function is given AJAX's response
// funcUponFailure: Optional failure function to execute, otherwise generic
//					 failure message is displayed using prependMainContent()
function sendAjaxRequest(action, postVars, funcAfterSuccess, funcUponFailure)
{
	varsToSend = 'action=' + urlencode(action);
	if("" != postVars) {
		varsToSend += '&' + urlencode(postVars);
	}
	
	$.ajax({
		url: 'phpjs.php',
		data: varsToSend,
		dataType: 'json',
		type: 'post',
		success: function (response) 
		{
			displayLoadingSplashScreen(false);
			var htmlContent = "";
			if(response.ok)
			{
				funcAfterSuccess(response);
			}
			else
			{
				if(funcUponFailure) {
					funcUponFailure(response);
				}
				else {
					prependMainContent(getDismissibleAlert("Error", response.msg, "error"), 5000);
				}
			}
		}
	}); 
}

// This function is called to initiate logout, which sends AJAX request to destroy the session and reload the page.
function performLogout()
{
	sendAjaxRequest("logout", "", function(r) {window.location.reload(false);} );
}

// This function is called to attempt a login which picks up Username and Password Form setup by index.php
function attempt_login()
{
	var username = $('#loginUsername').val();
	var postVars = 'username='+username  + '&password=' + $('#password').val();
	sendAjaxRequest("login", postVars, 
					function(response) {
						updateTopBar(response.navBarData);
						updateSideBar(response.sideBarData);
					});
}

function showRegistrationModal()
{
	var body = '<input class="span3" type="text" placeholder="Email" name="newReg_email" value="" id="newReg_email" /></BR>\
				<input class="span3" type="password" placeholder="Password" name="newReg_password" value="" id="newReg_password" /></BR>\
				<label>Your information</label>\
				<input class="span3" type="text" placeholder="First Name" name="newReg_firstName" value="" id="newReg_firstName" /></BR>\
				<input class="span3" type="text" placeholder="Last Name" name="newReg_lastName" value="" id="newReg_lastName" /></BR>';
				
	var heading = 	'<button class="btn btn-success" onClick="javascript: register_user()" name="submit"><i class="icon-share-alt icon-white"></i>&nbsp;<b>Register</b></button>\
					<button class="btn btn-warning" onClick="javascript: hidePopupModal()" name="submit"><i class="icon-remove icon-white"></i>&nbsp;<B>Cancel</b></button>';
					
	showPopupModal("Sign-Up", body, heading, "300");
}


// This returns a generic form with a textarea inside of it.
// the span is used to determine the span of the textarea
// contentAfterForm is any content to display after the form, such as a button
// textareaContents is what the textarea input should be set to.
function getGenericForm(textAreaDivID, span, contentAfterForm, textareaContents)
{
	var form = '<div class="row"><div class="span' + span+1 + '">';
	form  += 	    '<div class="alert alert-success">';
	form  += 		'<textarea  style="resize:none" id="' + textAreaDivID + '" name="' + textAreaDivID + '" class="span' + span + '">';
	if(textareaContents != undefined) 
		form  +=			textareaContents
		
	form  +=		'</textarea></br>';
	form  += 		contentAfterForm;
	form  += 		'</div>';
	form  += '</div></div>';
	return form;
}

// This function is called when a user initiates a search from NavBar
function search()
{
	var searchStr = $('#searchStr').val();
	sendAjaxRequest("searchProduct", "searchStr="+searchStr,
						 function(response) {
							alert("Search not implemented yet!");
						 });
}

function loadAllTestBeds()
{
	sendAjaxRequest("get_test_beds", "", 
					function(response) {
						updateMainContent("Load Testbed info here");
					});
}

