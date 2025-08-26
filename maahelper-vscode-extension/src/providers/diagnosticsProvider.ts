import * as vscode from 'vscode';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export class DiagnosticsProvider {
    private diagnosticCollection: vscode.DiagnosticCollection;
    private outputChannel: vscode.OutputChannel;

    constructor() {
        this.diagnosticCollection = vscode.languages.createDiagnosticCollection('maahelper');
        this.outputChannel = vscode.window.createOutputChannel('MaaHelper Diagnostics');
    }

    async analyzeDocument(document: vscode.TextDocument): Promise<void> {
        try {
            if (!this.isSupportedLanguage(document.languageId)) {
                return;
            }

            this.outputChannel.appendLine(`Analyzing document: ${document.fileName}`);

            // Get diagnostics from MaaHelper CLI
            const diagnostics = await this.getDiagnosticsFromCLI(document.fileName);
            
            // Convert to VSCode diagnostics
            const vscDiagnostics = this.convertToVSCodeDiagnostics(diagnostics);
            
            // Set diagnostics for the document
            this.diagnosticCollection.set(document.uri, vscDiagnostics);

        } catch (error) {
            this.outputChannel.appendLine(`Error analyzing document: ${error}`);
        }
    }

    private async getDiagnosticsFromCLI(filePath: string): Promise<any[]> {
        try {
            const { stdout } = await execAsync(`maahelper ide-analyze "${filePath}" --diagnostics`, {
                cwd: vscode.workspace.rootPath,
                timeout: 30000
            });

            const result = JSON.parse(stdout);
            return result.diagnostics || [];

        } catch (error) {
            this.outputChannel.appendLine(`CLI diagnostics error: ${error}`);
            return [];
        }
    }

    private convertToVSCodeDiagnostics(diagnostics: any[]): vscode.Diagnostic[] {
        return diagnostics.map(diag => {
            const range = new vscode.Range(
                Math.max(0, (diag.line || 0)),
                Math.max(0, (diag.column || 0)),
                Math.max(0, (diag.line || 0)),
                Math.max(0, (diag.column || 0) + (diag.length || 1))
            );

            const severity = this.convertSeverity(diag.severity);
            
            const vscDiagnostic = new vscode.Diagnostic(
                range,
                diag.message || 'Unknown issue',
                severity
            );

            vscDiagnostic.source = 'MaaHelper';
            
            if (diag.code) {
                vscDiagnostic.code = diag.code;
            }

            return vscDiagnostic;
        });
    }

    private convertSeverity(severity: string): vscode.DiagnosticSeverity {
        switch (severity?.toLowerCase()) {
            case 'error':
                return vscode.DiagnosticSeverity.Error;
            case 'warning':
                return vscode.DiagnosticSeverity.Warning;
            case 'info':
                return vscode.DiagnosticSeverity.Information;
            case 'hint':
                return vscode.DiagnosticSeverity.Hint;
            default:
                return vscode.DiagnosticSeverity.Information;
        }
    }

    private isSupportedLanguage(languageId: string): boolean {
        const supportedLanguages = [
            'python', 'javascript', 'typescript', 'java', 'cpp', 'c', 'csharp', 'go', 'rust'
        ];
        return supportedLanguages.includes(languageId);
    }

    public dispose(): void {
        this.diagnosticCollection.dispose();
        this.outputChannel.dispose();
    }
}
