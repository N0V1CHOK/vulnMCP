#!/bin/bash

echo "=================================================="
echo "   🎯 VulnMCP Setup Script 🎯"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Docker
echo -e "${YELLOW}Checking Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker found${NC}"

# Check Docker Compose
echo -e "${YELLOW}Checking Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose not found. Please install Docker Compose first.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose found${NC}"

# Setup data directory
echo -e "${YELLOW}Setting up data directories...${NC}"
chmod +x mcp-server/setup_data.sh
./mcp-server/setup_data.sh
echo -e "${GREEN}✅ Data directories created${NC}"

# Build and start containers
echo -e "${YELLOW}Building Docker containers...${NC}"
docker-compose build
echo -e "${GREEN}✅ Containers built${NC}"

echo -e "${YELLOW}Starting VulnMCP...${NC}"
docker-compose up -d
echo -e "${GREEN}✅ VulnMCP started${NC}"

# Wait for services
echo -e "${YELLOW}Waiting for services to start...${NC}"
sleep 5

# Check status
echo -e "${YELLOW}Checking service status...${NC}"
docker-compose ps

echo ""
echo "=================================================="
echo -e "${GREEN}   ✅ VulnMCP Setup Complete! ✅${NC}"
echo "=================================================="
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Open web interface: http://localhost:8080"
echo ""
echo "2. Configure Claude Desktop:"
echo "   Add to claude_desktop_config.json:"
echo ""
echo '   {' 
echo '     "mcpServers": {'
echo '       "vulnmcp": {'
echo '         "command": "docker",'
echo '         "args": ["exec", "-i", "vulnmcp-server", "python", "-m", "src.server"]'
echo '       }'
echo '     }'
echo '   }'
echo ""
echo "3. Restart Claude Desktop"
echo ""
echo "4. In Claude, use: vulnmcp_help"
echo ""
echo "🎮 Happy Hacking!"
echo ""
echo "View logs: docker-compose logs -f"
echo "Stop server: docker-compose down"
echo ""