#!/bin/bash

# AiEDA UV Build Script
# This script installs Python dependencies and aieda library using UV package manager

set -e  # Exit on any error

# Default values
PYTHON_CMD="python3"
PIP_INDEX="https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple"
VENV_DIR=".venv"
FORCE_REINSTALL=false
VERBOSE=false
SKIP_BUILD=false
INSTALL_DEV=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' 

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Install Python dependencies and aieda library using UV package manager

OPTIONS:
    --python PYTHON_CMD     Python command to use (default: python3)
    --pip-index INDEX_URL   PyPI index URL (default: Tsinghua mirror)
    --venv-dir DIR          Virtual environment directory (default: .venv)
    --force                 Force reinstall all dependencies
    --skip-build            Skip building aieda package
    --dev                   Install development dependencies
    --verbose               Verbose output
    -h, --help              Show this help message

EXAMPLES:
    $0                      # Install with default settings
    $0 --dev                # Install with development dependencies
    $0 --force              # Force reinstall everything

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --python)
            PYTHON_CMD="$2"
            shift 2
            ;;
        --pip-index)
            PIP_INDEX="$2"
            shift 2
            ;;
        --venv-dir)
            VENV_DIR="$2"
            shift 2
            ;;
        --force)
            FORCE_REINSTALL=true
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --dev)
            INSTALL_DEV=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Function to check system requirements
check_requirements() {
    print_info "Checking system requirements..."
    
    # Check Python
    if ! command -v "$PYTHON_CMD" &> /dev/null; then
        print_error "Python not found: $PYTHON_CMD"
        print_info "Please install Python 3.10+ or specify correct Python command with --python"
        exit 1
    fi
    
    # Check Python version
    local python_version=$("$PYTHON_CMD" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    local major=$(echo "$python_version" | cut -d. -f1)
    local minor=$(echo "$python_version" | cut -d. -f2)
    
    if [[ $major -lt 3 ]] || [[ $major -eq 3 && $minor -lt 10 ]]; then
        print_error "Python 3.10+ is required, found: $python_version"
        exit 1
    fi
    
    print_success "Python $python_version found"
    
    # Check git
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed"
        exit 1
    fi
}

# Function to install UV
install_uv() {
    if ! command -v uv &> /dev/null; then
        print_info "Installing UV package manager..."
        "$PYTHON_CMD" -m pip install uv
        print_success "UV installed successfully"
    else
        print_info "UV is already installed"
        if [[ "$VERBOSE" == "true" ]]; then
            uv --version
        fi
    fi
}

# Function to setup virtual environment
setup_venv() {
    print_info "Setting up virtual environment with UV..."
    
    # Remove existing environment if force reinstall
    if [[ "$FORCE_REINSTALL" == "true" ]] && [[ -d "$VENV_DIR" ]]; then
        print_info "Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
    fi
    
    # Create virtual environment
    if [[ ! -d "$VENV_DIR" ]]; then
        print_info "Creating virtual environment..."
        uv venv "$VENV_DIR"
    else
        print_info "Using existing virtual environment: $VENV_DIR"
    fi
    
    print_success "Virtual environment ready: $VENV_DIR"
}

# Function to build aieda package
build_package() {
    if [[ "$SKIP_BUILD" == "true" ]]; then
        print_warning "Skipping package build as requested"
        return 0
    fi
    
    print_info "Building aieda package..."
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Build the package
    print_info "Building wheel package..."
    uv build
    
    # Check if build was successful
    if [[ -d "dist" ]] && ls dist/*.whl &> /dev/null; then
        local wheel_file=$(ls dist/*.whl | head -n 1)
        print_success "Package built successfully: $wheel_file"
        return 0
    else
        print_error "Package build failed - no wheel file found"
        return 1
    fi
}

# Function to install aieda package
install_package() {
    print_info "Installing aieda package and dependencies..."
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Find the wheel file
    if [[ "$SKIP_BUILD" == "false" ]] && [[ -d "dist" ]] && ls dist/*.whl &> /dev/null; then
        local wheel_file=$(ls dist/*.whl | head -n 1)
        print_info "Installing from wheel: $wheel_file"
        
        local install_cmd="uv pip install $wheel_file"
        
        if [[ -n "$PIP_INDEX" ]]; then
            install_cmd="$install_cmd -i $PIP_INDEX"
        fi
        
        if [[ "$VERBOSE" == "true" ]]; then
            install_cmd="$install_cmd -v"
        fi
        
        print_info "Executing: $install_cmd"
        eval "$install_cmd"
    else
        # Install in development mode
        print_info "Installing in development mode..."
        local install_cmd="uv pip install -e ."
        
        if [[ "$INSTALL_DEV" == "true" ]]; then
            install_cmd="uv pip install -e .[dev,test,notebook]"
            print_info "Installing with development dependencies"
        fi
        
        if [[ -n "$PIP_INDEX" ]]; then
            install_cmd="$install_cmd -i $PIP_INDEX"
        fi
        
        if [[ "$VERBOSE" == "true" ]]; then
            install_cmd="$install_cmd -v"
        fi
        
        print_info "Executing: $install_cmd"
        eval "$install_cmd"
    fi
    
    print_success "aieda package installed successfully"
}

# Function to show package info
show_package_info() {
    print_info "Checking installed package..."
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Show aieda package info
    if python -c "import aieda" &> /dev/null; then
        local version=$(python -c "import aieda; print(getattr(aieda, '__version__', 'unknown'))")
        print_success "aieda package installed successfully (version: $version)"
    else
        print_warning "aieda package import failed"
    fi
    
    # Show installed packages
    if [[ "$VERBOSE" == "true" ]]; then
        print_info "Installed packages:"
        uv pip list
    fi
}

# Main execution
print_info "Starting AiEDA UV build process"
print_info "Configuration:"
print_info "  Python: $PYTHON_CMD"
print_info "  Virtual environment: $VENV_DIR"
print_info "  PyPI index: $PIP_INDEX"
print_info "  Install dev dependencies: $INSTALL_DEV"
print_info "  Skip package build: $SKIP_BUILD"
echo

# Execute build steps
check_requirements
install_uv
setup_venv
build_package
install_package
show_package_info
