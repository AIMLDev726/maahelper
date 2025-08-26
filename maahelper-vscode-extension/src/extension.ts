import * as vscode from 'vscode';
import { LanguageClient, LanguageClientOptions, ServerOptions } from 'vscode-languageclient/node';
import { MaaHelperProvider } from './providers/maahelperProvider';
import { WorkflowManager } from './workflow/workflowManager';
import { DiagnosticsProvider } from './providers/diagnosticsProvider';

let client: LanguageClient;
let maahelperProvider: MaaHelperProvider;
let workflowManager: WorkflowManager;
let diagnosticsProvider: DiagnosticsProvider;

export function activate(context: vscode.ExtensionContext) {
    console.log('MaaHelper extension is now active!');

    // Initialize providers
    maahelperProvider = new MaaHelperProvider();
    workflowManager = new WorkflowManager(context);
    diagnosticsProvider = new DiagnosticsProvider();

    // Start Language Server
    startLanguageServer(context);

    // Register commands
    registerCommands(context);

    // Setup event listeners
    setupEventListeners(context);

    // Show activation message
    vscode.window.showInformationMessage('MaaHelper AI Assistant is now active!');
}

function startLanguageServer(context: vscode.ExtensionContext) {
    const config = vscode.workspace.getConfiguration('maahelper');
    const cliPath = config.get<string>('cliPath', 'maahelper');

    // Server options - start the Python LSP server
    const serverOptions: ServerOptions = {
        command: cliPath,
        args: ['--lsp-server'],
        options: {
            cwd: vscode.workspace.rootPath
        }
    };

    // Client options
    const clientOptions: LanguageClientOptions = {
        documentSelector: [
            { scheme: 'file', language: 'python' },
            { scheme: 'file', language: 'javascript' },
            { scheme: 'file', language: 'typescript' },
            { scheme: 'file', language: 'java' },
            { scheme: 'file', language: 'cpp' },
            { scheme: 'file', language: 'c' }
        ],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.{py,js,ts,java,cpp,c,h}')
        }
    };

    // Create and start the language client
    client = new LanguageClient(
        'maahelperLanguageServer',
        'MaaHelper Language Server',
        serverOptions,
        clientOptions
    );

    context.subscriptions.push(client.start());
}

function registerCommands(context: vscode.ExtensionContext) {
    // Core analysis commands
    context.subscriptions.push(
        vscode.commands.registerCommand('maahelper.activate', () => {
            vscode.window.showInformationMessage('MaaHelper is already active!');
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('maahelper.analyzeFile', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active file to analyze');
                return;
            }
            await maahelperProvider.analyzeFile(editor.document);
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('maahelper.codeReview', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active file for code review');
                return;
            }
            await maahelperProvider.performCodeReview(editor.document, editor.selection);
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('maahelper.bugAnalysis', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active file for bug analysis');
                return;
            }
            await maahelperProvider.analyzeBugs(editor.document, editor.selection);
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('maahelper.refactorCode', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No code selected for refactoring');
                return;
            }
            await maahelperProvider.refactorCode(editor.document, editor.selection);
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('maahelper.explainCode', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No code selected to explain');
                return;
            }
            await maahelperProvider.explainCode(editor.document, editor.selection);
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('maahelper.generateTests', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active file for test generation');
                return;
            }
            await maahelperProvider.generateTests(editor.document, editor.selection);
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('maahelper.optimizePerformance', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No code selected for optimization');
                return;
            }
            await maahelperProvider.optimizePerformance(editor.document, editor.selection);
        })
    );

    // Workflow commands
    context.subscriptions.push(
        vscode.commands.registerCommand('maahelper.startWorkflow', async () => {
            await workflowManager.startWorkflow();
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('maahelper.showWorkflows', async () => {
            await workflowManager.showActiveWorkflows();
        })
    );
}

function setupEventListeners(context: vscode.ExtensionContext) {
    const config = vscode.workspace.getConfiguration('maahelper');
    
    // Auto-analysis on file save
    if (config.get<boolean>('autoAnalysis', false)) {
        context.subscriptions.push(
            vscode.workspace.onDidSaveTextDocument(async (document) => {
                if (isSupportedLanguage(document.languageId)) {
                    await diagnosticsProvider.analyzeDocument(document);
                }
            })
        );
    }

    // Configuration changes
    context.subscriptions.push(
        vscode.workspace.onDidChangeConfiguration((event) => {
            if (event.affectsConfiguration('maahelper')) {
                // Restart language server if CLI path changed
                if (event.affectsConfiguration('maahelper.cliPath')) {
                    restartLanguageServer(context);
                }
            }
        })
    );
}

function isSupportedLanguage(languageId: string): boolean {
    const supportedLanguages = ['python', 'javascript', 'typescript', 'java', 'cpp', 'c'];
    return supportedLanguages.includes(languageId);
}

async function restartLanguageServer(context: vscode.ExtensionContext) {
    if (client) {
        await client.stop();
    }
    startLanguageServer(context);
}

export function deactivate(): Thenable<void> | undefined {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
