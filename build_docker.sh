#!/bin/bash

# AIEDA Docker Build Script
# This script builds the AIEDA Docker image and runs the test

set -e

echo "Building AIEDA Docker images..."

# Build base image
echo "Step 1: Building base image..."
docker build -f Dockerfile.base -t aieda:base .

# Build final image
echo "Step 2: Building final image with iEDA..."
docker build -f Dockerfile.final -t aieda:latest .

echo "Docker images built successfully!"
echo ""
echo "To run the test, use:"
echo "  docker run --rm -it aieda:latest"
echo ""
echo "To run interactively:"
echo "  docker run --rm -it aieda:latest /bin/bash"
echo ""
echo "To run a specific test:"
echo "  docker run --rm -it aieda:latest python3 test/test_sky130_gcd.py"