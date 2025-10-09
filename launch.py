#!/usr/bin/env python3
"""
AI Vibe Chat Launcher - Choose between CLI and Web interface
"""

import sys
import subprocess
from pathlib import Path

def show_menu():
    print("🌀 AI Vibe Chat Launcher")
    print("=" * 40)
    print("Choose your interface:")
    print()
    print("1. 🌐 Web Interface (Modern GUI)")
    print("   - Beautiful chat interface")
    print("   - Real-time messaging")
    print("   - Multiple personalities")
    print("   - Save/load conversations")
    print()
    print("2. 💻 CLI Interface (Terminal)")
    print("   - Command-line chat")
    print("   - Colored output")
    print("   - Typing indicators")
    print("   - Full command system")
    print()
    print("3. ❌ Exit")
    print()

def launch_web():
    print("🚀 Launching Web Interface...")
    print("📱 Opening browser to http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "run_web.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Web interface stopped!")
    except Exception as e:
        print(f"❌ Error launching web interface: {e}")

def launch_cli():
    print("🚀 Launching CLI Interface...")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "-m", "ai_vibe_chat.cli", "--personality", "rizz"], check=True)
    except KeyboardInterrupt:
        print("\n👋 CLI interface stopped!")
    except Exception as e:
        print(f"❌ Error launching CLI interface: {e}")

def main():
    while True:
        show_menu()
        
        try:
            choice = input("Enter your choice (1-3): ").strip()
            
            if choice == "1":
                launch_web()
                break
            elif choice == "2":
                launch_cli()
                break
            elif choice == "3":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
                print()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print()

if __name__ == "__main__":
    main()
