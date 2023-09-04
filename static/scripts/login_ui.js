let isLogin = true;  // To track whether user is in login or signup mode

function loginWithFirebase() {
    var email = document.getElementById("email").value;
    var password = document.getElementById("password").value;

    if (isLogin) {
        firebase.auth().signInWithEmailAndPassword(email, password)
            .then((userCredential) => {
                var user = userCredential.user;
                user.getIdToken().then((token) => {
                    Wave.emit('token_received', {token: token});
                });
            })
            .catch((error) => {
                alert("Error signing in: " + error.message);
            });
    } else {
        firebase.auth().createUserWithEmailAndPassword(email, password)
            .then((userCredential) => {
                // Signed up successfully
                var user = userCredential.user;
                user.getIdToken().then((token) => {
                    Wave.emit('token_received', {token: token});
                });
            })
            .catch((error) => {
                alert("Error signing up: " + error.message);
            });
    }
}

