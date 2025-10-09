#!/usr/bin/env python3
"""
Launch the AI Vibe Chat Web Interface
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from ai_vibe_chat.web_app import app

if __name__ == "__main__":
    print("🚀 Starting AI Vibe Chat Web Interface...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Create saved_conversations directory in project root
    project_root = Path(__file__).parent
    saved_dir = project_root / 'saved_conversations'
    saved_dir.mkdir(exist_ok=True)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
