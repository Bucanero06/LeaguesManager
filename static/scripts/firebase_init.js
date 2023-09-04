// Script
// Initialize Firebase
var firebaseConfig = {FIREBASE_CONFIG};
// Initialize Firebase
firebase.initializeApp(firebaseConfig);

firebase.analytics();

// Get a reference to the database service
var database = firebase.database();

// Get a reference to the storage service
var storage = firebase.storage();

// Get a reference to the auth service
var auth = firebase.auth();

// Get a reference to the firestore service
var firestore = firebase.firestore();

// Get a reference to the functions service
var functions = firebase.functions();

// Print out information to know that initialization is complete
console.log("Firebase initialized");