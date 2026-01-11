#!/bin/bash

echo "🔧 Setting up VulnMCP data files..."

# Create directories
mkdir -p data/flags
mkdir -p data/progress
mkdir -p data/database

# Create flag files
echo "FLAG{MCP_T00L_1NJ3CT10N_M4ST3R}" > data/flags/level1.txt
echo "FLAG{MCP_R3S0URC3_UR1_H4CK3D}" > data/flags/level2.txt
echo "FLAG{C0NT3XT_P01S0N1NG_PR0}" > data/flags/level3.txt
echo "FLAG{PR0MPT_CH41N_M4ST3R_2024}" > data/flags/level4.txt
echo "FLAG{T00L_CH41N_PR1V_3SC}" > data/flags/level5.txt
echo "FLAG{S4MPL1NG_M4N1PUL4T10N_PR0}" > data/flags/level6.txt
echo "FLAG{PR0T0C0L_1NJ3CT10N_N1NJ4}" > data/flags/level7.txt
echo "FLAG{R00T_L1ST1NG_L34K_PR0}" > data/flags/level8.txt

# Create .gitkeep files
touch data/flags/.gitkeep
touch data/progress/.gitkeep
touch data/database/.gitkeep

echo "✅ Data files created successfully!"