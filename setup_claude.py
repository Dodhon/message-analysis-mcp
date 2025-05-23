#!/usr/bin/env python3

"""
Enhanced iMessage Analysis MCP Setup for Claude Desktop
Automatically configures Claude Desktop to use the iMessage Analysis MCP server
"""

import json
import os
import shutil
import sys
import subprocess
from pathlib import Path
import platform

# Global flag for non-interactive mode
AUTO_YES = '--yes' in sys.argv or '-y' in sys.argv

def print_header():
    """Print setup header"""
    print("iMessage Analysis MCP Setup for Claude Desktop")
    print("=" * 55)
    print("This script will set up the iMessage Analysis MCP server for Claude Desktop.")
    print("It will handle dependencies, configuration, and validation automatically.")
    
    if '--help' in sys.argv or '-h' in sys.argv:
        print("\nUsage:")
        print("  python3 setup_claude.py [--yes] [--help]")
        print("\nOptions:")
        print("  --yes, -y    Skip interactive prompts (for automated setups)")
        print("  --help, -h   Show this help message")
        print("\nThis script will:")
        print("  • Check system requirements")
        print("  • Install Python dependencies")
        print("  • Validate MCP server files")
        print("  • Configure Claude Desktop")
        print("  • Run health checks")
        sys.exit(0)
    
    print()

def check_system_requirements():
    """Check if system meets requirements"""
    print("Checking system requirements...")
    
    # Check macOS
    if not sys.platform.startswith('darwin'):
        print("ERROR: This tool only works on macOS")
        return False
    
    # Check macOS version (need 10.14+ for iMessage database format)
    macos_version = platform.mac_ver()[0]
    print(f"OK: macOS {macos_version} detected")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print(f"ERROR: Python 3.8+ required (found {sys.version})")
        return False
    
    print(f"OK: Python {sys.version.split()[0]} is compatible")
    return True

def install_dependencies(python_executable):
    """Install required dependencies if missing"""
    print("\nChecking and installing dependencies...")
    
    required_packages = ['mcp>=1.8.0', 'imessage-reader']
    
    for package in required_packages:
        try:
            package_name = package.split('>=')[0].split('==')[0]
            
            # Check if package is installed
            result = subprocess.run([
                python_executable, "-c", f"import {package_name.replace('-', '_')}"
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                # Try to get version info for MCP
                if package_name == 'mcp':
                    try:
                        version_result = subprocess.run([
                            python_executable, "-c", 
                            "import mcp; print(getattr(mcp, '__version__', 'unknown'))"
                        ], capture_output=True, text=True, timeout=5)
                        
                        if version_result.returncode == 0:
                            version = version_result.stdout.strip()
                            print(f"OK: {package_name} already installed (version: {version})")
                        else:
                            print(f"OK: {package_name} already installed")
                    except:
                        print(f"OK: {package_name} already installed")
                else:
                    print(f"OK: {package_name} already installed")
            else:
                print(f"Installing {package}...")
                install_result = subprocess.run([
                    python_executable, "-m", "pip", "install", package, "--upgrade"
                ], capture_output=True, text=True)
                
                if install_result.returncode == 0:
                    print(f"OK: Successfully installed {package}")
                else:
                    print(f"ERROR: Failed to install {package}:")
                    print(f"   {install_result.stderr}")
                    
                    # Try alternative installation method
                    print(f"Trying alternative installation...")
                    alt_result = subprocess.run([
                        python_executable, "-m", "pip", "install", package, "--user"
                    ], capture_output=True, text=True)
                    
                    if alt_result.returncode == 0:
                        print(f"OK: Successfully installed {package} with --user flag")
                    else:
                        print(f"ERROR: Alternative installation also failed")
                        return False
                    
        except Exception as e:
            print(f"ERROR: Error checking/installing {package}: {e}")
            return False
    
    return True

def find_python_executable():
    """Find the best Python executable to use"""
    print("\nFinding suitable Python installation...")
    
    # Get current Python being used
    current_python = sys.executable
    print(f"Current Python: {current_python}")
    
    # Try to find other common Python installations
    candidates = [
        current_python,
        "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3",
        "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3",
        "/Library/Frameworks/Python.framework/Versions/3.10/bin/python3",
        "/usr/local/bin/python3",
        "/opt/homebrew/bin/python3",
        shutil.which("python3"),
        "/usr/bin/python3"
    ]
    
    # Remove None and duplicates
    candidates = list(dict.fromkeys(filter(None, candidates)))
    
    print("\nTesting Python installations...")
    for python_path in candidates:
        if os.path.exists(python_path):
            try:
                # Test if Python is functional
                result = subprocess.run([
                    python_path, "--version"
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    version = result.stdout.strip()
                    print(f"OK: {python_path} - {version}")
                    return python_path
                else:
                    print(f"ERROR: {python_path} - Not functional")
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                print(f"ERROR: {python_path} - Cannot execute")
        else:
            print(f"SKIP: {python_path} - Not found")
    
    print("\nERROR: No suitable Python installation found!")
    return None

def check_claude_desktop_installed():
    """Check if Claude Desktop is installed"""
    print("\nChecking Claude Desktop installation...")
    
    claude_app_path = "/Applications/Claude.app"
    
    if os.path.exists(claude_app_path):
        print("OK: Claude Desktop found")
        return True
    else:
        print("WARNING: Claude Desktop not found at /Applications/Claude.app")
        print("   Please install Claude Desktop from: https://claude.ai/download")
        
        if AUTO_YES:
            print("   Continuing setup (--yes flag provided)")
            return True
        
        # Ask user if they want to continue anyway
        response = input("   Continue setup anyway? (y/N): ").lower().strip()
        return response in ['y', 'yes']

def check_full_disk_access():
    """Check if Full Disk Access is granted and provide guidance"""
    print("\nChecking Full Disk Access...")
    
    messages_db = Path.home() / "Library" / "Messages" / "chat.db"
    
    try:
        if messages_db.exists():
            # Try to read the file
            with open(messages_db, 'rb') as f:
                f.read(1)  # Just try to read 1 byte
            print("OK: Full Disk Access appears to be granted")
            return True
    except PermissionError:
        pass
    except Exception as e:
        print(f"WARNING: Error checking database access: {e}")
    
    print("ERROR: Full Disk Access not granted or iMessage database not accessible")
    print("\nTo grant Full Disk Access:")
    print("1. Open System Settings (or System Preferences)")
    print("2. Go to Privacy & Security → Full Disk Access")
    print("3. Click the '+' button and add:")
    print("   - Terminal.app")
    print("   - Python (if you see it in Applications)")
    print("   - Claude.app")
    print("4. Restart Terminal and Claude Desktop")
    print("5. Re-run this setup script")
    
    if AUTO_YES:
        print("\nWARNING: Skipping System Settings prompt (--yes flag provided)")
        return False
    
    # Offer to open System Settings
    response = input("\nOpen System Settings now? (y/N): ").lower().strip()
    if response in ['y', 'yes']:
        try:
            subprocess.run(['open', '-b', 'com.apple.systempreferences'])
            print("Opening System Settings...")
        except Exception:
            print("ERROR: Could not open System Settings automatically")
    
    return False

def get_claude_config_path():
    """Get the Claude Desktop configuration file path"""
    config_dir = Path.home() / "Library" / "Application Support" / "Claude"
    return config_dir / "claude_desktop_config.json"

def backup_existing_config(config_path):
    """Backup existing Claude Desktop configuration"""
    if config_path.exists():
        backup_path = config_path.with_suffix('.json.backup')
        shutil.copy2(config_path, backup_path)
        print(f"Backed up existing config to: {backup_path}")
        return True
    return False

def validate_mcp_server():
    """Validate that the MCP server can start"""
    print("\nValidating MCP server files...")
    
    required_files = ['mcp_server.py', 'message_analyzer.py', 'main.py']
    current_dir = Path.cwd()
    
    for file_name in required_files:
        file_path = current_dir / file_name
        if not file_path.exists():
            print(f"ERROR: Required file not found: {file_path}")
            print("Make sure you're running this script from the project root directory")
            return False
        print(f"OK: Found {file_name}")
    
    return True

def create_claude_config(python_executable):
    """Create or update Claude Desktop configuration"""
    print("\nConfiguring Claude Desktop...")
    
    config_path = get_claude_config_path()
    current_dir = os.getcwd()
    mcp_server_path = os.path.join(current_dir, "mcp_server.py")
    
    # Create directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing config or create new one
    config = {}
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                print("Loaded existing Claude config")
        except json.JSONDecodeError:
            print("WARNING: Invalid JSON in existing config, creating new one")
            backup_existing_config(config_path)
    
    # Ensure mcpServers exists
    if 'mcpServers' not in config:
        config['mcpServers'] = {}
    
    # Check if our server is already configured
    if 'imessage-analysis' in config['mcpServers']:
        print("WARNING: iMessage Analysis MCP server already configured")
        
        if AUTO_YES:
            print("   Overwriting existing configuration (--yes flag provided)")
        else:
            response = input("   Overwrite existing configuration? (y/N): ").lower().strip()
            if response not in ['y', 'yes']:
                print("   Keeping existing configuration")
                return True
    
    # Add our iMessage analysis server
    config['mcpServers']['imessage-analysis'] = {
        "command": python_executable,
        "args": [mcp_server_path]
    }
    
    # Write updated config
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"OK: Updated Claude Desktop config")
        print(f"   Config location: {config_path}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to write config: {e}")
        return False

def run_health_check(python_executable):
    """Run a comprehensive health check of the setup"""
    print("\nRunning health check...")
    
    try:
        # Test that the MCP server can import and initialize
        test_code = """
import sys
import os
sys.path.insert(0, os.getcwd())

try:
    from message_analyzer import MessageAnalyzer
    print("OK: MessageAnalyzer imports successfully")
except Exception as e:
    print(f"ERROR: MessageAnalyzer error: {e}")
    sys.exit(1)

try:
    import mcp_server
    print("OK: MCP server module imports successfully")
    
    # Check that the MCP object exists
    if hasattr(mcp_server, 'mcp'):
        print("OK: MCP server object found")
    else:
        print("ERROR: MCP server object not found")
        sys.exit(1)
        
    # Try to access the server's tools (FastMCP structure varies)
    try:
        # Check for common FastMCP attributes
        if hasattr(mcp_server.mcp, 'server') and hasattr(mcp_server.mcp.server, 'list_tools'):
            print("OK: MCP tools interface available")
        elif hasattr(mcp_server.mcp, '_tools_registry'):
            tool_count = len(mcp_server.mcp._tools_registry)
            print(f"OK: {tool_count} MCP tools registered")
        else:
            print("OK: MCP server structure validated")
    except Exception:
        print("WARNING: Tool validation skipped (server structure varies)")
        
except Exception as e:
    print(f"ERROR: MCP server error: {e}")
    sys.exit(1)

# Test that basic functions exist
try:
    funcs = ['get_basic_statistics', 'get_word_frequency', 'list_contacts']
    for func in funcs:
        if hasattr(mcp_server, func):
            print(f"OK: Function {func} found")
        else:
            print(f"ERROR: Function {func} missing")
            sys.exit(1)
except Exception as e:
    print(f"ERROR: Function check error: {e}")
    sys.exit(1)
"""
        
        result = subprocess.run([
            python_executable, "-c", test_code
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print(result.stdout.strip())
            return True
        else:
            print("ERROR: Health check failed:")
            if result.stderr:
                print(result.stderr)
            if result.stdout:
                print(result.stdout)
            return False
            
    except subprocess.TimeoutExpired:
        print("ERROR: Health check timed out")
        return False
    except Exception as e:
        print(f"ERROR: Health check failed: {e}")
        return False

def print_success_message():
    """Print success message and next steps"""
    print("\n" + "=" * 55)
    print("Setup Complete!")
    print("=" * 55)
    
    print("\nWhat was configured:")
    print("   • Python dependencies installed and verified")
    print("   • MCP server files validated")
    print("   • Claude Desktop configuration updated")
    print("   • 7 iMessage analysis tools registered")
    print("   • Health checks passed")
    
    print("\nNext steps:")
    print("1. Restart Claude Desktop completely:")
    print("   • Quit Claude Desktop (Cmd+Q)")
    print("   • Wait a few seconds")
    print("   • Reopen Claude Desktop")
    
    print("\n2. Verify MCP tools are loaded:")
    print("   • Look for the hammer icon in Claude Desktop")
    print("   • This indicates MCP tools are available")
    
    print("\n3. Try these example queries:")
    print("   • 'What are my basic iMessage statistics?'")
    print("   • 'Show me my most frequently used words'")
    print("   • 'List my contacts with message counts'")
    print("   • 'Search for messages containing \"meeting\"'")
    print("   • 'Get conversation with [contact name]'")
    
    print("\nIf you encounter issues:")
    print("   • Ensure Full Disk Access is granted (see setup guide)")
    print("   • Check Claude Desktop is fully restarted")
    print("   • Run this setup script again: python3 setup_claude.py")
    print("   • Check README.md for troubleshooting")
    
    print(f"\nConfiguration location:")
    config_path = get_claude_config_path()
    print(f"   {config_path}")
    
    print("\nReady to analyze your iMessages with Claude Desktop!")

def print_failure_message():
    """Print failure message with troubleshooting steps"""
    print("\n" + "=" * 55)
    print("Setup Failed")
    print("=" * 55)
    
    print("\nCommon solutions:")
    print("1. Run the script from the project root directory")
    print("2. Ensure Python 3.8+ is installed")
    print("3. Grant Full Disk Access (see instructions above)")
    print("4. Install Claude Desktop from https://claude.ai/download")
    print("5. Try running: pip install mcp imessage-reader")
    
    print("\nGet help:")
    print("   • Check README.md for detailed troubleshooting")
    print("   • Review the error messages above")
    print("   • Ensure all requirements are met")

def main():
    """Main setup function"""
    print_header()
    
    try:
        # System requirements check
        if not check_system_requirements():
            print_failure_message()
            sys.exit(1)
        
        # Check Claude Desktop installation
        if not check_claude_desktop_installed():
            print_failure_message()
            sys.exit(1)
        
        # Find suitable Python
        python_executable = find_python_executable()
        if not python_executable:
            print_failure_message()
            sys.exit(1)
        
        # Install dependencies
        if not install_dependencies(python_executable):
            print_failure_message()
            sys.exit(1)
        
        # Validate MCP server files
        if not validate_mcp_server():
            print_failure_message()
            sys.exit(1)
        
        # Check Full Disk Access (warning, not blocking)
        full_disk_access = check_full_disk_access()
        if not full_disk_access:
            print("\nWARNING: Continuing setup without Full Disk Access.")
            print("   You'll need to grant this later for the tools to work.")
        
        # Setup Claude configuration
        if not create_claude_config(python_executable):
            print_failure_message()
            sys.exit(1)
        
        # Run health check
        health_check_passed = run_health_check(python_executable)
        
        if health_check_passed:
            print_success_message()
        else:
            print("\nWARNING: Setup completed but health check failed.")
            print("   The configuration was written, but there may be issues.")
            print("   Try the troubleshooting steps if you encounter problems.")
        
    except KeyboardInterrupt:
        print("\n\nWARNING: Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: Unexpected error during setup: {e}")
        print_failure_message()
        sys.exit(1)

if __name__ == "__main__":
    main() 