import * as vscode from 'vscode';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export class MaaHelperProvider {
    private outputChannel: vscode.OutputChannel;

    constructor() {
        this.outputChannel = vscode.window.createOutputChannel('MaaHelper');
    }

    async analyzeFile(document: vscode.TextDocument): Promise<void> {
        try {
            this.outputChannel.show();
            this.outputChannel.appendLine(`Analyzing file: ${document.fileName}`);

            const result = await this.executeMaaHelperCommand('file-search', [document.fileName]);
            
            // Show results in a new document
            const analysisDoc = await vscode.workspace.openTextDocument({
                content: result,
                language: 'markdown'
            });
            
            await vscode.window.showTextDocument(analysisDoc, vscode.ViewColumn.Beside);
            
        } catch (error) {
            this.showError('File Analysis', error);
        }
    }

    async performCodeReview(document: vscode.TextDocument, selection?: vscode.Selection): Promise<void> {
        try {
            this.outputChannel.show();
            this.outputChannel.appendLine('Performing AI code review...');

            const code = selection ? document.getText(selection) : document.getText();
            const language = document.languageId;
            
            const result = await this.executeMaaHelperCommand('code-review', [], {
                code,
                language,
                file: document.fileName
            });

            await this.showResultInPanel('Code Review Results', result);
            
        } catch (error) {
            this.showError('Code Review', error);
        }
    }

    async analyzeBugs(document: vscode.TextDocument, selection?: vscode.Selection): Promise<void> {
        try {
            this.outputChannel.show();
            this.outputChannel.appendLine('Analyzing potential bugs...');

            const code = selection ? document.getText(selection) : document.getText();
            const language = document.languageId;
            
            const result = await this.executeMaaHelperCommand('bug-analysis', [], {
                code,
                language,
                file: document.fileName
            });

            await this.showResultInPanel('Bug Analysis Results', result);
            
        } catch (error) {
            this.showError('Bug Analysis', error);
        }
    }

    async refactorCode(document: vscode.TextDocument, selection: vscode.Selection): Promise<void> {
        try {
            if (selection.isEmpty) {
                vscode.window.showWarningMessage('Please select code to refactor');
                return;
            }

            this.outputChannel.show();
            this.outputChannel.appendLine('Refactoring selected code...');

            const code = document.getText(selection);
            const language = document.languageId;
            
            const result = await this.executeMaaHelperCommand('refactor-code', [], {
                code,
                language,
                file: document.fileName
            });

            // Show refactored code and ask if user wants to apply it
            const choice = await vscode.window.showInformationMessage(
                'Refactoring suggestions ready. View results?',
                'View Results',
                'Apply Changes',
                'Cancel'
            );

            if (choice === 'View Results') {
                await this.showResultInPanel('Refactoring Suggestions', result);
            } else if (choice === 'Apply Changes') {
                // Extract the refactored code from the result and apply it
                await this.applyRefactoredCode(document, selection, result);
            }
            
        } catch (error) {
            this.showError('Code Refactoring', error);
        }
    }

    async explainCode(document: vscode.TextDocument, selection: vscode.Selection): Promise<void> {
        try {
            if (selection.isEmpty) {
                vscode.window.showWarningMessage('Please select code to explain');
                return;
            }

            this.outputChannel.show();
            this.outputChannel.appendLine('Explaining selected code...');

            const code = document.getText(selection);
            const language = document.languageId;
            
            const result = await this.executeMaaHelperCommand('explain-concept', [], {
                code,
                language,
                context: 'code_explanation'
            });

            await this.showResultInPanel('Code Explanation', result);
            
        } catch (error) {
            this.showError('Code Explanation', error);
        }
    }

    async generateTests(document: vscode.TextDocument, selection?: vscode.Selection): Promise<void> {
        try {
            this.outputChannel.show();
            this.outputChannel.appendLine('Generating tests...');

            const code = selection ? document.getText(selection) : document.getText();
            const language = document.languageId;
            
            const result = await this.executeMaaHelperCommand('implement-feature', [], {
                code,
                language,
                task: 'generate_tests',
                file: document.fileName
            });

            await this.showResultInPanel('Generated Tests', result);
            
        } catch (error) {
            this.showError('Test Generation', error);
        }
    }

    async optimizePerformance(document: vscode.TextDocument, selection?: vscode.Selection): Promise<void> {
        try {
            this.outputChannel.show();
            this.outputChannel.appendLine('Analyzing performance optimization opportunities...');

            const code = selection ? document.getText(selection) : document.getText();
            const language = document.languageId;
            
            const result = await this.executeMaaHelperCommand('optimize-performance', [], {
                code,
                language,
                file: document.fileName
            });

            await this.showResultInPanel('Performance Optimization', result);
            
        } catch (error) {
            this.showError('Performance Optimization', error);
        }
    }

    private async executeMaaHelperCommand(command: string, args: string[] = [], data?: any): Promise<string> {
        const config = vscode.workspace.getConfiguration('maahelper');
        const cliPath = config.get<string>('cliPath', 'maahelper');
        
        let cmdArgs = [command, ...args];
        
        if (data) {
            // For complex data, we'll use stdin
            cmdArgs.push('--stdin');
        }

        const fullCommand = `${cliPath} ${cmdArgs.join(' ')}`;
        
        try {
            const { stdout, stderr } = await execAsync(fullCommand, {
                input: data ? JSON.stringify(data) : undefined,
                cwd: vscode.workspace.rootPath,
                timeout: 30000 // 30 second timeout
            });

            if (stderr) {
                this.outputChannel.appendLine(`Warning: ${stderr}`);
            }

            return stdout;
        } catch (error: any) {
            throw new Error(`MaaHelper command failed: ${error.message}`);
        }
    }

    private async showResultInPanel(title: string, content: string): Promise<void> {
        const panel = vscode.window.createWebviewPanel(
            'maahelperResults',
            title,
            vscode.ViewColumn.Beside,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        panel.webview.html = this.getWebviewContent(title, content);
    }

    private getWebviewContent(title: string, content: string): string {
        return `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>${title}</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: var(--vscode-foreground);
                    background-color: var(--vscode-editor-background);
                    padding: 20px;
                }
                pre {
                    background-color: var(--vscode-textBlockQuote-background);
                    padding: 10px;
                    border-radius: 4px;
                    overflow-x: auto;
                }
                code {
                    background-color: var(--vscode-textBlockQuote-background);
                    padding: 2px 4px;
                    border-radius: 2px;
                }
                h1, h2, h3 {
                    color: var(--vscode-textLink-foreground);
                }
            </style>
        </head>
        <body>
            <h1>${title}</h1>
            <div>${this.formatContent(content)}</div>
        </body>
        </html>`;
    }

    private formatContent(content: string): string {
        // Convert markdown-like content to HTML
        return content
            .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }

    private async applyRefactoredCode(document: vscode.TextDocument, selection: vscode.Selection, result: string): Promise<void> {
        // Extract code from the result (this would need to be more sophisticated)
        const codeMatch = result.match(/```\w*\n([\s\S]*?)```/);
        if (codeMatch) {
            const refactoredCode = codeMatch[1];
            const edit = new vscode.WorkspaceEdit();
            edit.replace(document.uri, selection, refactoredCode);
            await vscode.workspace.applyEdit(edit);
            vscode.window.showInformationMessage('Code refactoring applied successfully!');
        } else {
            vscode.window.showWarningMessage('Could not extract refactored code from result');
        }
    }

    private showError(operation: string, error: any): void {
        const message = `${operation} failed: ${error.message}`;
        this.outputChannel.appendLine(message);
        vscode.window.showErrorMessage(message);
    }
}
