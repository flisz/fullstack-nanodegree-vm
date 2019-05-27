function loadAsync(src, callback){
    var script = document.createElement('script');
    script.src = src; 
    script.type = 'text/javascript';
    script.async = true;
    if(callback != null){
        if (script.readyState) { // IE, incl. IE9
            script.onreadystatechange = function() {
                if (script.readyState == "loaded" || script.readyState == "complete") {
                    script.onreadystatechange = null;
                    callback();
                }
            };
        } else {
            script.onload = function() { // Other browsers
                callback();
            };
        }
    }
    a=document.getElementsByTagName('script')[0];
    a.parentNode.insertBefore(script,a);
}

loadAsync("https://www.example.com/script.js", callbackFunction);

function callbackFunction() {
    console.log('Callback function run');
}

// Enter an API key from the Google API Console:
//   https://console.developers.google.com/apis/credentials
  // var apiKey = 'YOUR_API_KEY';
// Enter the API Discovery Docs that describes the APIs you want to
// access. In this example, we are accessing the People API, so we load
// Discovery Doc found here: https://developers.google.com/people/api/rest/
  // var discoveryDocs = ["https://people.googleapis.com/$discovery/rest?version=v1"];
// Enter a client ID for a web application from the Google API Console:
//   https://console.developers.google.com/apis/credentials?project=_
// In your API Console project, add a JavaScript origin that corresponds
//   to the domain where you will be running the script.
var clientId = '{{login_session.get("oauth_client_id")}}';
// Enter one or more authorization scopes. Refer to the documentation for
// the API or https://developers.google.com/people/v1/how-tos/authorizing
// for details.
var scopes = 'profile';

var signInButton = document.getElementById('signin-button');
var signOutButton = document.getElementById('signout-button');
var signOutDiv = document.getElementById('signout-div');

function handleClientLoad() {
  // Loads the client library and the auth2 library together for efficiency.
  // Loading the auth2 library is optional here since `gapi.client.init` function will load
  // it if not already loaded. Loading it upfront can save one network request.
  gapi.load('client:auth2', initClient);
}

function initClient() {
  // Initialize the client with API key and People API, and initialize OAuth with an
  // OAuth 2.0 client ID and scopes (space delimited string) to request access.
  gapi.client.init({
      //apiKey: 'YOUR_API_KEY', ***** if needed, will add. 
      //discoveryDocs: ["https://people.googleapis.com/$discovery/rest?version=v1"],
      clientId: clientId,
      scope: scopes
  }).then(function () {
    // Listen for sign-in state changes.
    gapi.auth2.getAuthInstance().isSignedIn.listen(updateSigninStatus);

    // Handle the initial sign-in state.
    updateSigninStatus(gapi.auth2.getAuthInstance().isSignedIn.get());
    
    signInButton.onclick = handleSignInClick;
    signOutButton.onclick = handleSignOutClick;
  });
}

function updateSigninStatus(isSignedIn) {
  // When signin status changes, this function is called.
  // If the signin status is changed to signedIn, we make an API call.
  if (isSignedIn) {
    signInButton.style.display = 'none';
    signOutDiv.style.display = 'block';
    makeApiCall();
  } else {
    signInButton.style.display = 'block';
    signOutDiv.style.display = 'none';
  }
}

function handleSignInClick(event) {
  // Ideally the button should only show up after gapi.client.init finishes, so that this
  // handler won't be called before OAuth is initialized.
  gapi.auth2.getAuthInstance().signIn();
}

function handleSignOutClick(event) {
  serverEndSession();
  gapi.auth2.getAuthInstance().signOut();
}

function makeApiCall() {
  // Make an API call to the People API, and print the user's given name.
  var googleUser = gapi.auth2.getAuthInstance().currentUser.get()
  var profile = googleUser.getBasicProfile();
  console.log('ID: ' + profile.getId()); // Do not send to your backend! Use an ID token instead.
  console.log('Name: ' + profile.getName());
  console.log('Image URL: ' + profile.getImageUrl());
  console.log('Email: ' + profile.getEmail()); // This is null if the 'email' scope is not present.
    sendApiCallError(reason)          
  );
}

function sendApiCallError(reason) {
  console.log('Error: ' + reason.result.error.message);
  var userIcon = document.getElementById("userIcon");
  var userPicture = "{{ url_for('static', filename='jpeg/error_icon.jpeg') }}";
  var userName = 'Google Sign In Error: ' + reason.result.error.message;
  userIcon.src = userPicture;
  userIcon.alt = userName;  
}

//my code: 
function sendToken() {
  var googleUser = gapi.auth2.getAuthInstance().currentUser.get()
  var id_token = googleUser.getAuthResponse().id_token;
  var send_this = {
    'id_token' : id_token,
  }
  if (id_token) {
    $.ajax(
      {
        type: 'POST',
        url: '/google-connect?state={{login_session.get("state")}}',
        processData: false,
        data: JSON.stringify(send_this),
        contentType: 'application/json; charset=utf-8',
        success: sendTokenSuccess(result)                
      } 
    ); 
  }
}

function sendTokenSuccess(result) {
  console.log("sendTokenSuccess-result:"+result);
  var userIcon = document.getElementById("userIcon");
  var userPicture = "{{login_session.get('picture')}}";
  var userName = "{{login_session.get('username')}}";
  if (userPicture) {
    userIcon.src = userPicture;
  }
  if (userName) {
    userIcon.alt = userName;  
  }
  console.log(userIcon);
}

function serverEndSession() {
  var googleUser = gapi.auth2.getAuthInstance().currentUser.get()
  var id_token = googleUser.getAuthResponse().id_token;
  var send_this = {
    'id_token' : id_token,
  }
  if (id_token) {
    $.ajax(
      {
        type: 'POST',
        url: '/google-disconnect?state={{login_session.get("state")}}',
        processData: false,
        data: JSON.stringify(send_this),
        contentType: 'application/json; charset=utf-8',
        success: sendDisconnectSuccess(result)                
      } 
    ); 
  }
}

function sendDisconnectSuccess(result) {
  console.log("sendDisconnectSuccess-result:"+result);
  signInButton.style.display = 'block';
  signOutDiv.style.display = 'none';
}