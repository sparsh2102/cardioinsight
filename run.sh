#!/bin/bash
# CardioInsight — One-Click Setup Script
# Run this once to set up everything from scratch

echo ""
echo "============================================"
echo "   CardioInsight — Setup Script"
echo "   Heart Disease Risk Assessment System"
echo "   By Satyam Kumar & Sparsh Goyal"
echo "============================================"
echo ""

# Step 1 — Install dependencies
echo "[1/4] Installing Python dependencies..."
pip install -r requirements.txt --break-system-packages -q
echo "      Done."

# Step 2 — Generate dataset
echo "[2/4] Generating 10,000 patient records..."
python generate_data.py
echo "      Done."

# Step 3 — Train ML model
echo "[3/4] Training Random Forest ML model..."
python train_model.py
echo "      Done."

# Step 4 — Generate charts
echo "[4/4] Generating analytics charts..."
python charts.py
echo "      Done."

echo ""
echo "============================================"
echo "   Setup complete! Starting server..."
echo "   Open: http://localhost:5000"
echo "============================================"
echo ""

python app.py
