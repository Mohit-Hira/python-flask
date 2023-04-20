'use strict';
window.addEventListener('load', function () {
 console.log("Hello World!");
 document.getElementById('sign-out').onclick = function() {
    // ask firebase to sign out the user
    fetch('https://calendar-381809.el.r.appspot.com/signout').then((res)=>{
        firebase.auth().signOut();
        console.log(res.json())
    })
   
   };

   
   var uiConfig = {
    signInSuccessUrl: '/',
    signInOptions: [
    firebase.auth.EmailAuthProvider.PROVIDER_ID
    ]
   };

   
   firebase.auth().onAuthStateChanged(function(user) {
    if(user) {
    // document.getElementById('sign-out').hidden = false;
    // document.getElementById('continue').hidden = false;
    // document.getElementById('login-info').hidden = false;
    console.log(`Signed in as ${user.displayName} (${user.email})`);
    user.getIdToken().then(function(token) {
    document.cookie = "token=" + token;
    }).then(()=>{
        document.getElementById('sign-out').hidden = false;
        document.getElementById('continue').hidden = false;
        document.getElementById('login-info').hidden = false;
    })

    } 
    
    else {
    var ui = new firebaseui.auth.AuthUI(firebase.auth());
    ui.start('#firebase-auth-container', uiConfig);
    document.getElementById('sign-out').hidden = true;
    document.getElementById('continue').hidden = true;
    document.getElementById('login-info').hidden = true;
    document.cookie = "token=";
    }
    }, function(error) {
    console.log(error);
    alert('Unable to log in: ' + error);
    });
   
});
