# Sentry-AI VS Code Extension

AI-powered automation assistant for VS Code. Automatically handle dialogs with vision AI.

## Features

- **Start/Stop Controls**: Control Sentry-AI directly from VS Code
- **Real-time Monitoring**: See live activity in the sidebar
- **Activity Log**: Track all automated actions
- **Statistics**: View actions performed today
- **Status Bar**: Quick status overview
- **Notifications**: Optional popup notifications for each action
- **Settings**: Full configuration from VS Code settings

## Installation

### Prerequisites

1. **Sentry-AI Installed**: Make sure Sentry-AI is installed and configured
   ```bash
   cd /path/to/Sentry-AI
   pip install -r requirements.txt
   ```

2. **Python Environment**: Python 3.9+ with required dependencies

### Install Extension

#### Option 1: From VSIX (Recommended)

1. Package the extension:
   ```bash
   cd vscode-extension
   npm install
   npm run package
   npx vsce package
   ```

2. Install in VS Code:
   - Open VS Code
   - Go to Extensions (⌘+Shift+X)
   - Click "..." menu → "Install from VSIX"
   - Select `sentry-ai-1.2.0.vsix`

#### Option 2: Development Mode

1. Open extension folder in VS Code:
   ```bash
   cd vscode-extension
   code .
   ```

2. Press F5 to launch Extension Development Host

## Usage

### Quick Start

1. **Open Command Palette**: ⌘+Shift+P (Mac) or Ctrl+Shift+P (Windows/Linux)
2. **Type**: "Sentry-AI: Start Automation"
3. **Done!**: Sentry-AI is now running in the background

### Sidebar Panel

Click the robot icon (🤖) in the Activity Bar to open Sentry-AI panel:

- **Status**: Current running status
- **Activity Log**: Real-time list of automated actions
- **Statistics**: Actions performed today

### Status Bar

Bottom-right corner shows Sentry-AI status:
- **Active**: `$(robot) Sentry-AI: Active` (orange background)
- **Inactive**: `$(robot) Sentry-AI: Inactive` (normal background)

Click to view detailed status.

### Commands

All commands are available via Command Palette (⌘+Shift+P):

- `Sentry-AI: Start Automation` - Start Sentry-AI
- `Sentry-AI: Stop Automation` - Stop Sentry-AI
- `Sentry-AI: Restart` - Restart Sentry-AI
- `Sentry-AI: Show Status` - Open status panel
- `Sentry-AI: Show Activity Logs` - Open log file
- `Sentry-AI: Open Settings` - Open extension settings

## Configuration

### Settings

Open VS Code settings and search for "Sentry-AI":

#### `sentry-ai.enabled`
- **Type**: boolean
- **Default**: `true`
- Enable/disable Sentry-AI automation

#### `sentry-ai.autoStart`
- **Type**: boolean
- **Default**: `false`
- Automatically start Sentry-AI when VS Code opens

#### `sentry-ai.pythonPath`
- **Type**: string
- **Default**: `""`
- Path to Python executable (leave empty for system Python)
- Example: `/usr/local/bin/python3`

#### `sentry-ai.sentryPath`
- **Type**: string
- **Default**: `""`
- Path to Sentry-AI installation directory
- Example: `/Users/username/Sentry-AI`

#### `sentry-ai.showNotifications`
- **Type**: boolean
- **Default**: `true`
- Show popup notifications when dialogs are handled

#### `sentry-ai.logLevel`
- **Type**: string (DEBUG | INFO | WARNING | ERROR)
- **Default**: `"INFO"`
- Logging verbosity level

#### `sentry-ai.observerInterval`
- **Type**: number
- **Default**: `2.0`
- Dialog check interval in seconds

### Example Configuration

```json
{
  "sentry-ai.enabled": true,
  "sentry-ai.autoStart": true,
  "sentry-ai.pythonPath": "/usr/local/bin/python3",
  "sentry-ai.sentryPath": "/Users/mikail/Sentry-AI",
  "sentry-ai.showNotifications": true,
  "sentry-ai.logLevel": "INFO",
  "sentry-ai.observerInterval": 2.0
}
```

## How It Works

1. **Extension Starts**: When VS Code opens or you run start command
2. **Spawns Process**: Launches Sentry-AI Python process in background
3. **Monitors Output**: Captures stdout/stderr from Sentry-AI
4. **Parses Logs**: Extracts activity and updates UI
5. **Shows Notifications**: Optional popup for each action
6. **Updates Views**: Real-time activity log and statistics

## Features in Detail

### Activity Log

Real-time list of all automated actions:
- Application name (e.g., "Visual Studio Code")
- Action taken (e.g., "clicked 'Yes'")
- Timestamp
- Automatically updates when new actions occur
- Keeps last 50 actions

### Statistics

Current statistics:
- **Actions Today**: Total actions performed since midnight
- **Status**: Running or Stopped
- **Last Activity**: Most recent automated action

### Status Panel

Detailed status view showing:
- Current running state
- Actions today count
- Last activity
- Configuration summary
- Feature list
- Management buttons

## Troubleshooting

### Extension Won't Start

1. **Check Python Path**:
   ```bash
   which python3
   ```
   Set this path in settings

2. **Check Sentry-AI Path**:
   ```bash
   ls /path/to/Sentry-AI/sentry_ai/main.py
   ```
   Set correct path in settings

3. **Check Dependencies**:
   ```bash
   cd /path/to/Sentry-AI
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### No Activity Showing

1. **Check if Running**: Status bar should show "Active"
2. **Check Logs**: Use "Sentry-AI: Show Activity Logs" command
3. **Trigger a Dialog**: Create a dialog in VS Code to test
4. **Check Notifications**: Enable in settings

### High CPU Usage

1. **Increase Observer Interval**: Set to 3.0 or 5.0 seconds
2. **Disable Auto-Start**: Only run when needed
3. **Check Log Level**: Set to WARNING or ERROR

### Extension Not Loading

1. **Reload VS Code**: ⌘+Shift+P → "Reload Window"
2. **Check Developer Tools**: Help → Toggle Developer Tools → Console
3. **Reinstall Extension**: Uninstall and reinstall VSIX

## Development

### Build Extension

```bash
cd vscode-extension
npm install
npm run compile
```

### Package Extension

```bash
npm install -g vsce
vsce package
```

### Debug Extension

1. Open `vscode-extension` folder in VS Code
2. Press F5 to launch Extension Development Host
3. Test commands and features
4. Check Debug Console for logs

## Requirements

- VS Code 1.85.0 or higher
- Python 3.9 or higher
- Sentry-AI installed and configured

## Known Issues

- Extension may need restart after changing settings
- Log monitoring may have slight delay (1-2 seconds)
- First start may take 5-10 seconds

## Roadmap

- [ ] One-click Sentry-AI installation
- [ ] Built-in Python environment
- [ ] Visual dialog preview
- [ ] Action history timeline
- [ ] Custom automation rules
- [ ] Multi-app configuration
- [ ] Export statistics to CSV

## Support

- **Issues**: https://github.com/lekesiz/Sentry-AI/issues
- **Documentation**: https://github.com/lekesiz/Sentry-AI

## License

MIT License - See LICENSE file in Sentry-AI repository

## Credits

Built with:
- **TypeScript** - Language
- **VS Code Extension API** - Integration
- **Webpack** - Bundling
- **Claude Opus 4** - Vision AI

---

**Version**: 1.2.0
**Author**: Sentry-AI Team
**Powered by**: Claude Opus 4 Vision AI

Generated with [Claude Code](https://claude.com/claude-code)
