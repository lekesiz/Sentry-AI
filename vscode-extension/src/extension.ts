import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { spawn, ChildProcess } from 'child_process';

let sentryProcess: ChildProcess | null = null;
let statusBarItem: vscode.StatusBarItem;
let activityTreeProvider: ActivityLogProvider;
let statsTreeProvider: StatsProvider;
let isRunning = false;
let actionsToday = 0;
let lastActivity: string | null = null;

export function activate(context: vscode.ExtensionContext) {
    console.log('Sentry-AI extension is now active');

    // Create status bar item
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.command = 'sentry-ai.showStatus';
    context.subscriptions.push(statusBarItem);
    updateStatusBar();

    // Register tree data providers
    activityTreeProvider = new ActivityLogProvider();
    statsTreeProvider = new StatsProvider();

    vscode.window.registerTreeDataProvider('sentry-ai-activity', activityTreeProvider);
    vscode.window.registerTreeDataProvider('sentry-ai-stats', statsTreeProvider);

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('sentry-ai.start', startSentryAI),
        vscode.commands.registerCommand('sentry-ai.stop', stopSentryAI),
        vscode.commands.registerCommand('sentry-ai.restart', restartSentryAI),
        vscode.commands.registerCommand('sentry-ai.showStatus', showStatus),
        vscode.commands.registerCommand('sentry-ai.showLogs', showLogs),
        vscode.commands.registerCommand('sentry-ai.settings', openSettings)
    );

    // Auto-start if enabled
    const config = vscode.workspace.getConfiguration('sentry-ai');
    if (config.get('autoStart')) {
        startSentryAI();
    }

    // Start log monitoring
    startLogMonitoring(context);
}

export function deactivate() {
    stopSentryAI();
}

function startSentryAI() {
    if (isRunning) {
        vscode.window.showWarningMessage('Sentry-AI is already running');
        return;
    }

    const config = vscode.workspace.getConfiguration('sentry-ai');
    const sentryPath = config.get<string>('sentryPath') || path.join(__dirname, '..', '..');
    const pythonPath = config.get<string>('pythonPath') || 'python3';

    // Check if sentry-ai directory exists
    const sentryMainPath = path.join(sentryPath, 'sentry_ai', 'main.py');
    if (!fs.existsSync(sentryMainPath)) {
        vscode.window.showErrorMessage(
            `Sentry-AI not found at ${sentryPath}. Please set the correct path in settings.`
        );
        return;
    }

    try {
        // Determine actual Python path (venv or system)
        let actualPythonPath = pythonPath;

        // If pythonPath is relative or just "python3", try venv first
        if (!path.isAbsolute(pythonPath)) {
            const venvPython = path.join(sentryPath, 'venv', 'bin', 'python');
            if (fs.existsSync(venvPython)) {
                actualPythonPath = venvPython;
                console.log(`Using venv Python: ${actualPythonPath}`);
            }
        }

        console.log(`Starting Sentry-AI with Python: ${actualPythonPath}`);
        console.log(`Working directory: ${sentryPath}`);

        // Start Sentry-AI process
        sentryProcess = spawn(actualPythonPath, ['-m', 'sentry_ai.main'], {
            cwd: sentryPath,
            env: {
                ...process.env,
                PYTHONPATH: sentryPath
            }
        });

        sentryProcess.stdout?.on('data', (data) => {
            const output = data.toString();
            console.log(`[Sentry-AI] ${output}`);
            parseLogOutput(output);
        });

        sentryProcess.stderr?.on('data', (data) => {
            const output = data.toString();
            console.error(`[Sentry-AI Error] ${output}`);

            // Show critical errors
            if (output.includes('Error') || output.includes('Failed')) {
                vscode.window.showErrorMessage(`Sentry-AI: ${output}`);
            }
        });

        sentryProcess.on('exit', (code) => {
            console.log(`Sentry-AI exited with code ${code}`);
            isRunning = false;
            updateStatusBar();

            if (code !== 0) {
                vscode.window.showErrorMessage(`Sentry-AI stopped with error code ${code}`);
            }
        });

        isRunning = true;
        updateStatusBar();
        vscode.window.showInformationMessage('Sentry-AI started successfully');

    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to start Sentry-AI: ${error.message}`);
        console.error(error);
    }
}

function stopSentryAI() {
    if (!isRunning || !sentryProcess) {
        vscode.window.showWarningMessage('Sentry-AI is not running');
        return;
    }

    try {
        sentryProcess.kill();
        sentryProcess = null;
        isRunning = false;
        updateStatusBar();
        vscode.window.showInformationMessage('Sentry-AI stopped');
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to stop Sentry-AI: ${error.message}`);
    }
}

function restartSentryAI() {
    stopSentryAI();
    setTimeout(() => startSentryAI(), 1000);
}

function updateStatusBar() {
    if (isRunning) {
        statusBarItem.text = `$(robot) Sentry-AI: Active`;
        statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
        statusBarItem.tooltip = `Sentry-AI is monitoring\nActions today: ${actionsToday}\nLast: ${lastActivity || 'None'}`;
    } else {
        statusBarItem.text = `$(robot) Sentry-AI: Inactive`;
        statusBarItem.backgroundColor = undefined;
        statusBarItem.tooltip = 'Sentry-AI is not running\nClick to see status';
    }
    statusBarItem.show();
}

function parseLogOutput(output: string) {
    // Parse log output and extract activity
    const config = vscode.workspace.getConfiguration('sentry-ai');
    const showNotifications = config.get<boolean>('showNotifications');

    // Detect successful actions
    if (output.includes('Successfully automated')) {
        actionsToday++;
        const match = output.match(/Successfully automated (.+?): clicked '(.+?)'/);
        if (match) {
            lastActivity = `${match[1]}: ${match[2]}`;
            activityTreeProvider.addActivity({
                app: match[1],
                action: match[2],
                time: new Date().toLocaleTimeString()
            });
            statsTreeProvider.updateStats(actionsToday);
            updateStatusBar();

            if (showNotifications) {
                vscode.window.showInformationMessage(
                    `Sentry-AI handled dialog in ${match[1]}`,
                    'Show Details'
                ).then(selection => {
                    if (selection === 'Show Details') {
                        showLogs();
                    }
                });
            }
        }
    }

    // Detect vision AI analysis
    if (output.includes('Vision AI detected dialog')) {
        const match = output.match(/Vision AI detected dialog in (.+)/);
        if (match) {
            lastActivity = `Vision: ${match[1]}`;
            activityTreeProvider.addActivity({
                app: match[1],
                action: 'Vision AI',
                time: new Date().toLocaleTimeString()
            });
            updateStatusBar();
        }
    }
}

function showStatus() {
    const config = vscode.workspace.getConfiguration('sentry-ai');
    const panel = vscode.window.createWebviewPanel(
        'sentryStatus',
        'Sentry-AI Status',
        vscode.ViewColumn.One,
        {}
    );

    panel.webview.html = `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    padding: 20px;
                    color: var(--vscode-foreground);
                }
                .status {
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                    background: var(--vscode-editor-background);
                }
                .running { border-left: 4px solid #4CAF50; }
                .stopped { border-left: 4px solid #f44336; }
                h2 { color: var(--vscode-textLink-foreground); }
                .stat {
                    display: flex;
                    justify-content: space-between;
                    padding: 8px 0;
                    border-bottom: 1px solid var(--vscode-panel-border);
                }
                button {
                    background: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    padding: 8px 16px;
                    margin: 5px;
                    cursor: pointer;
                    border-radius: 3px;
                }
                button:hover {
                    background: var(--vscode-button-hoverBackground);
                }
            </style>
        </head>
        <body>
            <h1>🤖 Sentry-AI Status</h1>

            <div class="status ${isRunning ? 'running' : 'stopped'}">
                <h2>${isRunning ? '✅ Running' : '❌ Stopped'}</h2>
                <div class="stat">
                    <span>Status:</span>
                    <strong>${isRunning ? 'Active' : 'Inactive'}</strong>
                </div>
                <div class="stat">
                    <span>Actions Today:</span>
                    <strong>${actionsToday}</strong>
                </div>
                <div class="stat">
                    <span>Last Activity:</span>
                    <strong>${lastActivity || 'None'}</strong>
                </div>
                <div class="stat">
                    <span>Auto Start:</span>
                    <strong>${config.get('autoStart') ? 'Enabled' : 'Disabled'}</strong>
                </div>
                <div class="stat">
                    <span>Observer Interval:</span>
                    <strong>${config.get('observerInterval')}s</strong>
                </div>
            </div>

            <div style="margin-top: 20px;">
                <button onclick="alert('Use Command Palette: Sentry-AI: Start')">Start</button>
                <button onclick="alert('Use Command Palette: Sentry-AI: Stop')">Stop</button>
                <button onclick="alert('Use Command Palette: Sentry-AI: Restart')">Restart</button>
            </div>

            <h2>📋 Features</h2>
            <ul>
                <li>✅ Vision AI with Claude Opus 4</li>
                <li>✅ Automatic dialog detection</li>
                <li>✅ Mouse & keyboard automation</li>
                <li>✅ Real-time activity logging</li>
                <li>✅ VS Code integration</li>
            </ul>

            <h2>⚙️ Configuration</h2>
            <p>Open settings to configure Sentry-AI behavior:</p>
            <ul>
                <li>Auto-start on VS Code launch</li>
                <li>Python path (if not in system PATH)</li>
                <li>Sentry-AI installation directory</li>
                <li>Notification preferences</li>
                <li>Log level</li>
            </ul>
        </body>
        </html>
    `;
}

function showLogs() {
    const config = vscode.workspace.getConfiguration('sentry-ai');
    const sentryPath = config.get<string>('sentryPath') || path.join(__dirname, '..', '..');
    const logPath = path.join(sentryPath, 'sentry_ai.log');

    if (fs.existsSync(logPath)) {
        vscode.workspace.openTextDocument(logPath).then(doc => {
            vscode.window.showTextDocument(doc, vscode.ViewColumn.Two);
        });
    } else {
        vscode.window.showWarningMessage('Log file not found');
    }
}

function openSettings() {
    vscode.commands.executeCommand('workbench.action.openSettings', 'sentry-ai');
}

function startLogMonitoring(context: vscode.ExtensionContext) {
    // Monitor log file for changes
    const config = vscode.workspace.getConfiguration('sentry-ai');
    const sentryPath = config.get<string>('sentryPath') || path.join(__dirname, '..', '..');
    const logPath = path.join(sentryPath, 'sentry_ai.log');

    if (fs.existsSync(logPath)) {
        const watcher = fs.watch(logPath, (eventType) => {
            if (eventType === 'change') {
                // Read last few lines of log
                try {
                    const content = fs.readFileSync(logPath, 'utf-8');
                    const lines = content.split('\n').slice(-10);
                    lines.forEach(line => parseLogOutput(line));
                } catch (error) {
                    console.error('Error reading log file:', error);
                }
            }
        });

        context.subscriptions.push({ dispose: () => watcher.close() });
    }
}

// Tree Data Provider for Activity Log
class ActivityLogProvider implements vscode.TreeDataProvider<ActivityItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<ActivityItem | undefined>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    private activities: ActivityItem[] = [];

    addActivity(activity: { app: string; action: string; time: string }) {
        this.activities.unshift(new ActivityItem(activity.app, activity.action, activity.time));
        if (this.activities.length > 50) {
            this.activities = this.activities.slice(0, 50);
        }
        this._onDidChangeTreeData.fire(undefined);
    }

    getTreeItem(element: ActivityItem): vscode.TreeItem {
        return element;
    }

    getChildren(): ActivityItem[] {
        return this.activities;
    }
}

class ActivityItem extends vscode.TreeItem {
    constructor(
        public readonly app: string,
        public readonly action: string,
        public readonly time: string
    ) {
        super(`${app}: ${action}`, vscode.TreeItemCollapsibleState.None);
        this.tooltip = `${app}\n${action}\nTime: ${time}`;
        this.description = time;
        this.iconPath = new vscode.ThemeIcon('check');
    }
}

// Tree Data Provider for Stats
class StatsProvider implements vscode.TreeDataProvider<StatItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<StatItem | undefined>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    private actionsToday = 0;

    updateStats(count: number) {
        this.actionsToday = count;
        this._onDidChangeTreeData.fire(undefined);
    }

    getTreeItem(element: StatItem): vscode.TreeItem {
        return element;
    }

    getChildren(): StatItem[] {
        return [
            new StatItem('Actions Today', this.actionsToday.toString(), 'number'),
            new StatItem('Status', isRunning ? 'Running' : 'Stopped', isRunning ? 'pass' : 'error'),
            new StatItem('Last Activity', lastActivity || 'None', 'clock')
        ];
    }
}

class StatItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly value: string,
        iconName: string
    ) {
        super(label, vscode.TreeItemCollapsibleState.None);
        this.description = value;
        this.iconPath = new vscode.ThemeIcon(iconName);
    }
}
