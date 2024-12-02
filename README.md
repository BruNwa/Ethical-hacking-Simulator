# 🛡️ Ethical Hacking Simulator

⚠️ **DISCLAIMER**

This project is strictly for educational purposes only. The techniques and tools demonstrated here are intended for learning cybersecurity concepts in a controlled environment. Do not use these techniques against systems you don't own or have explicit permission to test. Users are responsible for complying with applicable laws and regulations.

---

The Ethical Hacking Simulator is a comprehensive hands-on learning platform designed to help cybersecurity enthusiasts, students, and professionals practice common security scenarios in a safe environment. Through interactive simulations and real-time feedback, users can gain practical experience with phishing analysis, SQL injection, data breach prevention, and ransomware impact scenarios.

## 🌐 [Live Demo](https://ethical-hacking-simulator.vercel.app/)
Try out the application without backend hosting. Note that scenario execution requires full backend setup.

## ✨ Features

- 🎯 Real-time terminal emulation
- 🔒 Secure containerized environments
- 🎨 Beautiful, responsive UI with Rive animations
- 🌐 Cross-platform compatibility
- 📊 Session management and monitoring
- 🔄 Auto-cleanup of inactive environments

## 🎯 Training Scenarios

### Phishing Awareness Simulator
Educational platform for understanding phishing tactics. Participants analyze real-world phishing attempts, learn to identify suspicious emails, and track success rates through log analysis.

### SQL Injection Training
Hands-on training environment for SQL injection techniques using a vulnerable test database. Practice identifying injection points and understanding common attack patterns.

### Ransomware Impact Simulator
Safe simulation environment demonstrating ransomware attack impacts. Learn proper backup procedures, encryption/decryption processes, and incident response steps.

### Data Breach Prevention
Practical training on identifying and preventing data breaches. Covers port scanning, database user privilege analysis, and sensitive data detection.

## 🛠️ Tech Stack

### Frontend
- **Flutter** - UI framework
- **Rive** - Animations
- **Glassmorphism** - UI effects
- **Google Fonts** - Typography
- **HTTP** - API communication

### Backend
- **Flask** - Web framework
- **Docker** - Containerization
- **Redis** - Session management
- **MySQL** - Database scenarios

## 🚀 Setup & Installation

### Prerequisites
- Docker and Docker Compose

### Backend Setup
1. Clone the repository
```bash
git clone https://github.com/BruNwa/Ethical-hacking-Simulator.git
```

2. Start the Docker containers
```bash
docker-compose up -d
```

## 🔧 Configuration

### Docker Services
- **Backend**: Flask application (Port 5000)
- **Redis**: Session management (Port 6379)
- **Frontend**: Nginx server (Port 80)

### Network Configuration
- Isolated network: 172.22.0.0/16
- Backend: 172.22.0.2
- Redis: 172.22.0.3
- Frontend: 172.22.0.4

## 🔒 Security Features

- Containerized environments for each session
- Automated cleanup of inactive sessions
- Secure command execution
- Rate limiting
- Session timeout management

## 📱 Responsive Design

The application is fully responsive and works seamlessly across:
- 💻 Desktop browsers
- 📱 Mobile devices
- 🖥️ Tablets

## ⚡ Performance

- Resource limits per container:
  - Backend: CPU: 2 cores, Memory: 8GB
  - Frontend: CPU: 0.5 cores, Memory: 2GB

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 🙋‍♂️ Author

Made with ❤️ by [Anwar Zaim](https://www.linkedin.com/in/anwar-zaim)