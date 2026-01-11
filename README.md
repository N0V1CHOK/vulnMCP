#  VulnMCP

<div align="center">

![VulnMCP Logo](https://img.shields.io/badge/VulnMCP-Security%20Training-00ff00?style=for-the-badge)
![MCP](https://img.shields.io/badge/MCP-Protocol-purple?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Professional MCP Security Training Platform**

*Learn MCP security through hands-on exploitation of real vulnerabilities*

[Quick Start](#-quick-start) • [Challenges](#-challenges) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

##  IMPORTANT DISCLAIMER

**VulnMCP contains intentional security vulnerabilities for educational purposes.**

-  **DO NOT** deploy in production environments
-  **DO NOT** expose to untrusted networks  
-  **DO NOT** use on systems with real data
-  **DO** use in isolated learning environments
-  **DO** practice responsible disclosure
-  **DO** share knowledge to improve security

---

##  Features

-  **8 Progressive Challenges** - From beginner to expert
-  **MCP-Specific Vulnerabilities** - Real protocol exploitation
-  **Gamified Learning** - Points, badges, leaderboard
-  **Smart Hint System** - Progressive hints without spoilers
-  **Progress Tracking** - Monitor your improvement
-  **Docker Ready** - One command to start
-  **Comprehensive Docs** - Learn as you hack
-  **Beautiful Interface** - Terminal-style UI

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Claude Desktop (or any MCP client)
- Git

### Installation
```bash
# 1. Clone the repository
git clone https://github.com/YOUR_ORG/vulnmcp.git
cd vulnmcp

# 2. Start with Docker
docker-compose up -d

# 3. View logs
docker-compose logs -f vulnmcp-server

# 4. Open web interface
open http://localhost:8080
```

### Configure Claude Desktop

Add to your `claude_desktop_config.json`:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
```json
{
  "mcpServers": {
    "vulnmcp": {
      "command": "docker",
      "args": ["exec", "-i", "vulnmcp-server", "python", "-m", "src.server"]
    }
  }
}
```

### Start Hacking!

In Claude Desktop:
```
Use the tool: vulnmcp_help

To see all challenges:
vulnmcp_help(action='challenges')
```

---

## 🎯 Challenges

| Level | Name | Difficulty | Points | Category |
|-------|------|------------|--------|----------|
| 1 | Tool Parameter Injection | ⭐☆☆☆ | 100 | Input Validation |
| 2 | Resource URI Manipulation | ⭐☆☆☆ | 150 | Access Control |
| 3 | Context Poisoning | ⭐⭐☆☆ | 200 | Prompt Security |
| 4 | Prompt Injection Chain | ⭐⭐☆☆ | 250 | LLM Security |
| 5 | Tool Chaining Exploitation | ⭐⭐☆☆ | 300 | Logic Flaws |
| 6 | Sampling Manipulation | ⭐⭐⭐☆ | 350 | Protocol Abuse |
| 7 | Protocol Message Injection | ⭐⭐⭐☆ | 400 | Protocol Security |
| 8 | Root Listing Abuse | ⭐⭐⭐☆ | 350 | Info Disclosure |

**Total Points**: 2,100

---

## 📚 What You'll Learn

### MCP Security Fundamentals

-  Tool parameter validation and sanitization
-  Resource URI access control
-  Context separation between system and user data
-  Prompt injection prevention techniques
-  Tool chaining security implications
-  Protocol message validation
-  Capability enforcement
-  Information disclosure prevention

### Real-World Skills

-  Vulnerability Discovery
-  Exploitation Techniques
-  Secure Implementation
-  Security Documentation
-  Penetration Testing
-  Defense Strategies

---

## 🏆 Scoring & Achievements

### Scoring System

- **Base Points**: Each challenge has a base point value
- **Penalties**: -5 points per failed attempt
- **Hint Cost**: -10 to -100 points depending on hint level
- **Minimum Score**: 25% of base points guaranteed

### Badges

- 🩸 **First Blood** - Complete your first challenge
- 🦸 **No Hints Hero** - Complete 3+ challenges without hints
- ⚡ **Speed Demon** - Complete a challenge in ≤5 attempts
- 🎯 **Halfway There** - Complete 4 challenges
- 👑 **Champion** - Complete all 8 challenges
- 💯 **Perfect Score** - Get maximum points on all completed challenges

---

## 📖 Documentation

- [ Challenge Walkthroughs](docs/CHALLENGES.md)
- [ Setup Guide](docs/SETUP.md)
- [ Architecture](docs/ARCHITECTURE.md)
- [ Contributing](CONTRIBUTING.md)
- [ Security Policy](SECURITY.md)
- [ License](LICENSE)

---

## 🛠️ Development

### Local Development (No Docker)
```bash
# Setup Python environment
cd mcp-server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup data
chmod +x setup_data.sh
./setup_data.sh

# Run server
python -m src.server
```

### Project Structure
```
vulnmcp/
├── mcp-server/           # Main MCP server
│   ├── src/
│   │   ├── server.py     # Server orchestration
│   │   └── challenges/   # Challenge modules
├── web-interface/        # Web UI
├── data/                 # Flags & progress
├── docs/                 # Documentation
└── docker-compose.yml    # Docker config
```

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Ways to Contribute

-  Report bugs
-  Suggest new challenges
-  Improve documentation
-  Enhance UI/UX
-  Add tests
-  Translate content

---

## 📊 Statistics

- **8** Challenging Levels
- **2,100** Total Points Available
- **6** Achievement Badges
- **100%** MCP-Focused Vulnerabilities
- **0%** Generic Web Challenges

---

## 🙏 Acknowledgments

- Inspired by [DVWA](https://github.com/digininja/DVWA)
- Built for [Model Context Protocol](https://modelcontextprotocol.io)
- Created for security education and awareness

---

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## ⭐ Star Us!

If you find VulnMCP helpful, please star this repository!

---

<div align="center">

**Made with ❤️ for MCP Security Education**

[Report Bug](https://github.com/YOUR_ORG/vulnmcp/issues) • [Request Feature](https://github.com/YOUR_ORG/vulnmcp/issues)

</div>