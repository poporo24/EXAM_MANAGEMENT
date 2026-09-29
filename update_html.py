import os
import re

firebase_js = '''
<script type="module">
  import { initializeApp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js";
  import { getAuth, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";
  
  const firebaseConfig = {
    apiKey: "AIzaSyCjf-aMcch8I9thXy5Lw1QzWfUX3sOAwHE",
    authDomain: "cca-exam-system.firebaseapp.com",
    projectId: "cca-exam-system",
    storageBucket: "cca-exam-system.firebasestorage.app",
    messagingSenderId: "779356462475",
    appId: "1:779356462475:web:a9fae5792d5d73be45638e"
  };

  const app = initializeApp(firebaseConfig);
  const auth = getAuth(app);

  window.handleLogin = async function(e) {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const btn = document.getElementById('login-btn');
    const oldText = btn.innerHTML;
    
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Signing in...';
    btn.disabled = true;
    
    try {
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        const token = await userCredential.user.getIdToken();
        document.getElementById('firebase_token').value = token;
        document.getElementById('login-form').submit();
    } catch (error) {
        btn.innerHTML = oldText;
        btn.disabled = false;
        
        let msg = "Invalid email or password.";
        if (error.code === 'auth/user-not-found') msg = "No user found with this email.";
        if (error.code === 'auth/wrong-password') msg = "Incorrect password.";
        if (error.code === 'auth/too-many-requests') msg = "Account temporarily locked due to many failed attempts.";
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'p-4 rounded-md mb-6 text-sm bg-red-50 text-red-700 border border-red-200';
        errorDiv.innerText = msg;
        
        const form = document.getElementById('login-form');
        const existingError = form.previousElementSibling;
        if (existingError && existingError.className.includes('bg-red-50')) {
            existingError.remove();
        }
        form.parentNode.insertBefore(errorDiv, form);
    }
  }
</script>
'''

# Update login.html
login_path = 'template/login.html'
with open(login_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('</head>', firebase_js + '\n</head>')
content = content.replace('<form action="/login" method="POST" class="space-y-6">', '<form id="login-form" action="/login" method="POST" class="space-y-6" onsubmit="handleLogin(event)">\n<input type="hidden" name="firebase_token" id="firebase_token">')
content = content.replace('<button type="submit"', '<button type="submit" id="login-btn"')
with open(login_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated login.html")

forgot_js = '''
<script type="module">
  import { initializeApp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js";
  import { getAuth, sendPasswordResetEmail } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";
  
  const firebaseConfig = {
    apiKey: "AIzaSyCjf-aMcch8I9thXy5Lw1QzWfUX3sOAwHE",
    authDomain: "cca-exam-system.firebaseapp.com",
    projectId: "cca-exam-system",
    storageBucket: "cca-exam-system.firebasestorage.app",
    messagingSenderId: "779356462475",
    appId: "1:779356462475:web:a9fae5792d5d73be45638e"
  };

  const app = initializeApp(firebaseConfig);
  const auth = getAuth(app);

  window.handleReset = async function(e) {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const btn = document.getElementById('reset-btn');
    const oldText = btn.innerHTML;
    
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Sending...';
    btn.disabled = true;
    
    try {
        await sendPasswordResetEmail(auth, email);
        btn.innerHTML = oldText;
        btn.disabled = false;
        
        const successDiv = document.createElement('div');
        successDiv.className = 'p-4 rounded-md mb-6 text-sm bg-green-50 text-green-700 border border-green-200';
        successDiv.innerText = "Password reset email sent! Please check your inbox.";
        
        const form = document.getElementById('forgot-form');
        const existingMsg = form.previousElementSibling;
        if (existingMsg && existingMsg.className.includes('bg-')) {
            existingMsg.remove();
        }
        form.parentNode.insertBefore(successDiv, form);
        form.reset();
    } catch (error) {
        btn.innerHTML = oldText;
        btn.disabled = false;
        
        let msg = "Error sending email.";
        if (error.code === 'auth/user-not-found') msg = "No user found with this email.";
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'p-4 rounded-md mb-6 text-sm bg-red-50 text-red-700 border border-red-200';
        errorDiv.innerText = msg;
        
        const form = document.getElementById('forgot-form');
        const existingMsg = form.previousElementSibling;
        if (existingMsg && existingMsg.className.includes('bg-')) {
            existingMsg.remove();
        }
        form.parentNode.insertBefore(errorDiv, form);
    }
  }
</script>
'''

forgot_path = 'template/forgot_password.html'
with open(forgot_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('</head>', forgot_js + '\n</head>')
content = content.replace('<form action="/forgot_password" method="POST"', '<form id="forgot-form" action="#" class="space-y-6" onsubmit="handleReset(event)">')
content = content.replace('<button type="submit"', '<button type="submit" id="reset-btn"')
with open(forgot_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated forgot_password.html")
