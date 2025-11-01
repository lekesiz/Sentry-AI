#!/bin/bash
# Install Sentry-AI as macOS LaunchAgent for auto-start

PLIST_FILE="com.sentry-ai.daemon.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_PATH="$LAUNCH_AGENTS_DIR/$PLIST_FILE"

echo "🚀 Installing Sentry-AI Auto-Start Daemon"
echo "=========================================="

# Create LaunchAgents directory if it doesn't exist
if [ ! -d "$LAUNCH_AGENTS_DIR" ]; then
    echo "📁 Creating LaunchAgents directory..."
    mkdir -p "$LAUNCH_AGENTS_DIR"
fi

# Copy plist file
echo "📋 Copying launch agent configuration..."
cp "$PLIST_FILE" "$PLIST_PATH"

# Load the launch agent
echo "▶️  Loading Sentry-AI daemon..."
launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load "$PLIST_PATH"

# Check status
if launchctl list | grep -q "com.sentry-ai.daemon"; then
    echo ""
    echo "✅ Sentry-AI daemon installed successfully!"
    echo ""
    echo "📋 Status:"
    launchctl list | grep "com.sentry-ai.daemon"
    echo ""
    echo "📝 Logs:"
    echo "  - Output: ~/Sentry-AI/sentry_ai_daemon.log"
    echo "  - Errors: ~/Sentry-AI/sentry_ai_daemon_error.log"
    echo ""
    echo "🔧 Management Commands:"
    echo "  - Stop:    launchctl unload $PLIST_PATH"
    echo "  - Start:   launchctl load $PLIST_PATH"
    echo "  - Restart: launchctl kickstart -k gui/\$(id -u)/com.sentry-ai.daemon"
    echo "  - Status:  launchctl list | grep sentry-ai"
    echo ""
    echo "🎉 Sentry-AI will now start automatically on login!"
else
    echo ""
    echo "❌ Failed to install daemon"
    echo "Check logs for errors"
fi
