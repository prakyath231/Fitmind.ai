import os, json
config = {
    "mcpServers": {
        "fitmind": {
            "command": "C:\\Users\\91636\\Documents\\Fitmind.ai\\venv\\Scripts\\python.exe",
            "args": ["C:\\Users\\91636\\Documents\\Fitmind.ai\\mcp_server.py"],
            "cwd": "C:\\Users\\91636\\Documents\\Fitmind.ai"
        }
    }
}
path = os.path.join(os.environ['APPDATA'], 'Claude', 'claude_desktop_config.json')
with open(path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2)
print('Done!')
