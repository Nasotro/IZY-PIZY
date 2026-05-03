import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyDnEqYDloT75QeOGtDROI7aBvUizip-IUo",
  authDomain: "izy-pizy.firebaseapp.com",
  projectId: "izy-pizy",
  storageBucket: "izy-pizy.firebasestorage.app",
  messagingSenderId: "323013535227",
  appId: "1:323013535227:web:e9e5459c7f8412de41d75e"
};

export const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();