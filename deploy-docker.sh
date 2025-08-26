#!/bin/bash

# CUET UG Admission Analyzer - Docker Deployment Script
# This script helps you build and run your application with Docker

echo "🐳 CUET UG Admission Analyzer - Docker Deployment"
echo "================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first:"
    echo "  - Windows/Mac: https://docs.docker.com/desktop/"
    echo "  - Linux: https://docs.docker.com/engine/install/"
    exit 1
fi

print_success "Docker is installed"

# Check if Docker is running
if ! docker info &> /dev/null; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_success "Docker is running"

# Get application name
read -p "Enter your application name (default: cuet-analyzer): " APP_NAME
APP_NAME=${APP_NAME:-cuet-analyzer}

# Check if Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    print_error "Dockerfile not found in current directory"
    exit 1
fi

print_success "Dockerfile found"

echo ""
print_status "🏗️  Building Docker image: $APP_NAME"
echo "   This may take a few minutes..."

# Build Docker image
if docker build -t $APP_NAME .; then
    print_success "Docker image built successfully"
else
    print_error "Failed to build Docker image"
    exit 1
fi

echo ""
print_status "🚀 Starting application container..."

# Stop any existing container with the same name
docker stop $APP_NAME 2>/dev/null || true
docker rm $APP_NAME 2>/dev/null || true

# Run the container
if docker run -d \
    --name $APP_NAME \
    -p 8000:8000 \
    -v "$(pwd)/data:/app/data" \
    -v "$(pwd)/outputs:/app/outputs" \
    -v "$(pwd)/uploads:/app/uploads" \
    $APP_NAME; then
    
    print_success "Container started successfully"
    
    echo ""
    echo "🎉 Deployment Complete!"
    echo "================================================="
    echo "🌐 Application URL: http://localhost:8000"
    echo "📊 Health Check: http://localhost:8000/api/health"
    echo "📚 API Documentation: http://localhost:8000/docs"
    echo ""
    echo "🔧 Docker Commands:"
    echo "   View logs: docker logs $APP_NAME"
    echo "   Stop app: docker stop $APP_NAME"
    echo "   Start app: docker start $APP_NAME"
    echo "   Remove app: docker rm -f $APP_NAME"
    echo ""
    
    # Wait for application to start
    print_status "⏳ Waiting for application to start..."
    sleep 10
    
    # Check if application is responding
    if curl -f http://localhost:8000/api/health &> /dev/null; then
        print_success "Application is responding"
        
        # Ask if user wants to open browser
        read -p "Would you like to open the application in your browser? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # Try to open browser (works on most systems)
            if command -v xdg-open &> /dev/null; then
                xdg-open http://localhost:8000
            elif command -v open &> /dev/null; then
                open http://localhost:8000
            elif command -v start &> /dev/null; then
                start http://localhost:8000
            else
                echo "Please open http://localhost:8000 in your browser"
            fi
        fi
    else
        print_warning "Application might still be starting. Please wait a moment and try http://localhost:8000"
    fi
    
else
    print_error "Failed to start container"
    exit 1
fi

echo ""
print_success "🐳 Docker deployment completed successfully!"
print_status "Your CUET UG Admission Analyzer is now running in a container!"
