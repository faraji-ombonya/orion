"use strict";

// import firebase
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-app.js";
import {
  getAuth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
} from "https://www.gstatic.com/firebasejs/9.22.2/firebase-auth.js";

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCqfrc3DZAkBixKeF_wUGGIKH9ubcgl-rA",
  authDomain: "gallery-429016.firebaseapp.com",
  projectId: "gallery-429016",
  storageBucket: "gallery-429016.appspot.com",
  messagingSenderId: "964826913450",
  appId: "1:964826913450:web:4b5a9301e43ac0eb57ced3",
};

window.addEventListener("load", function () {
  const app = initializeApp(firebaseConfig);
  const auth = getAuth(app);
  updateUI(this.document.cookie);

  // signup new user to firebase
  this.document
    .getElementById("sign-up")
    .addEventListener("click", function () {
      const email = document.getElementById("email").value;
      const password = document.getElementById("password").value;

      createUserWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
          // user is created
          const user = userCredential.user;

          // get the id token for the user who just logged in and force a 
          // redirect to /
          user.getIdToken().then((token) => {
            document.cookie = "token=" + token + ";path=/;SameSite=Strict";
            window.location = "/";
          });
        })
        .catch((error) => {
          // log any error to the console
          console.log(error.code + error.message);
        });
    });

  // login of a user to firebase
  this.document.getElementById("login").addEventListener("click", function () {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    signInWithEmailAndPassword(auth, email, password)
      .then((userCredential) => {
        // user is signed in
        const user = userCredential.user;

        // get the ID token of the user who just logged in and force a 
        // redirect to /
        user.getIdToken().then((token) => {
          document.cookie = "token=" + token + ";path=/;SameSite=Strict";
          window.location = "/";
        });
      })
      .catch((error) => {
        // log any error to the console
        console.log(error.code + error.message);
      });
  });

  // signout from firebase
  this.document
    .getElementById("sign-out")
    .addEventListener("click", function () {
      signOut(auth).then((output) => {
        // remove the ID token for the user and force a redirect to /
        document.cookie = "token=;path=/;SameSite=Strict";
        window.location = "/";
      });
    });
});

// function will update the UI for the user depending on if they are logged
// in or notby checking the passed in cookie that contains the token
function updateUI(cookie) {
  var token = parseCookieToken(cookie);

  // if a user is logged in, the disable the email, password, signup and
  // login UI elements and show the signout button and vice versa
  if (token.length > 0) {
    document.getElementById("login-box").hidden = true;
    document.getElementById("sign-out").hidden = false;
  } else {
    document.getElementById("login-box").hidden = false;
    document.getElementById("sign-out").hidden = true;
  }
}

function parseCookieToken(cookie) {
  // split the cookie out on the basis of the semi colon
  var strings = cookie.split(";");

  // go through each of the strings
  for (let i = 0; i < strings.length; i++) {
    // split the string based on the = sign. if the LHS is token the return
    // the RHS immediately
    var temp = strings[i].split("=");
    if (temp[0].trim() == "token") return temp[1].trim();
  }

  // if we got to this point and the token wasn't in the cookie so return
  // the empty string
  return "";
}
