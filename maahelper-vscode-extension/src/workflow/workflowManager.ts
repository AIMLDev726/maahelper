import * as vscode from 'vscode';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export class WorkflowManager {
    private context: vscode.ExtensionContext;
    private outputChannel: vscode.OutputChannel;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.outputChannel = vscode.window.createOutputChannel('MaaHelper Workflows');
    }

    async startWorkflow(): Promise<void> {
        try {
            // Get available workflow templates
            const templates = await this.getWorkflowTemplates();
            
            if (templates.length === 0) {
                vscode.window.showWarningMessage('No workflow templates available');
                return;
            }

            // Show template selection
            const selectedTemplate = await vscode.window.showQuickPick(
                templates.map(t => ({
                    label: t.name,
                    description: t.description,
                    detail: `Category: ${t.category}`,
                    template: t
                })),
                {
                    placeHolder: 'Select a workflow template',
                    matchOnDescription: true,
                    matchOnDetail: true
                }
            );

            if (!selectedTemplate) {
                return;
            }

            // Collect inputs for the template
            const inputs = await this.collectTemplateInputs(selectedTemplate.template);
            
            // Create and execute workflow
            const workflowId = await this.createWorkflow(selectedTemplate.template.name, inputs);
            
            if (workflowId) {
                const choice = await vscode.window.showInformationMessage(
                    `Workflow created: ${workflowId}. Execute now?`,
                    'Execute',
                    'View Status',
                    'Cancel'
                );

                if (choice === 'Execute') {
                    await this.executeWorkflow(workflowId);
                } else if (choice === 'View Status') {
                    await this.showWorkflowStatus(workflowId);
                }
            }

        } catch (error) {
            vscode.window.showErrorMessage(`Failed to start workflow: ${error}`);
        }
    }

    async showActiveWorkflows(): Promise<void> {
        try {
            const workflows = await this.listWorkflows();
            
            if (workflows.length === 0) {
                vscode.window.showInformationMessage('No active workflows');
                return;
            }

            const selectedWorkflow = await vscode.window.showQuickPick(
                workflows.map(w => ({
                    label: w.name || w.id,
                    description: `Status: ${w.status}`,
                    detail: `Progress: ${w.progress || 'Unknown'}`,
                    workflow: w
                })),
                {
                    placeHolder: 'Select a workflow to manage',
                    matchOnDescription: true
                }
            );

            if (!selectedWorkflow) {
                return;
            }

            // Show workflow management options
            const action = await vscode.window.showQuickPick([
                { label: '📊 View Status', action: 'status' },
                { label: '▶️ Execute', action: 'execute' },
                { label: '⏸️ Pause', action: 'pause' },
                { label: '▶️ Resume', action: 'resume' },
                { label: '❌ Cancel', action: 'cancel' },
                { label: '📍 Create Checkpoint', action: 'checkpoint' },
                { label: '📋 View Checkpoints', action: 'list-checkpoints' }
            ], {
                placeHolder: 'Select an action'
            });

            if (!action) {
                return;
            }

            await this.executeWorkflowAction(selectedWorkflow.workflow.id, action.action);

        } catch (error) {
            vscode.window.showErrorMessage(`Failed to show workflows: ${error}`);
        }
    }

    private async getWorkflowTemplates(): Promise<any[]> {
        try {
            const { stdout } = await execAsync('maahelper workflow-templates --json', {
                cwd: vscode.workspace.rootPath
            });
            
            return JSON.parse(stdout);
        } catch (error) {
            console.error('Failed to get workflow templates:', error);
            return [];
        }
    }

    private async listWorkflows(): Promise<any[]> {
        try {
            const { stdout } = await execAsync('maahelper workflow-list --json', {
                cwd: vscode.workspace.rootPath
            });
            
            return JSON.parse(stdout);
        } catch (error) {
            console.error('Failed to list workflows:', error);
            return [];
        }
    }

    private async createWorkflow(templateName: string, inputs: any): Promise<string | null> {
        try {
            const inputsJson = JSON.stringify(inputs);
            const { stdout } = await execAsync(
                `maahelper workflow-create "${templateName}" --inputs '${inputsJson}'`,
                { cwd: vscode.workspace.rootPath }
            );
            
            // Extract workflow ID from output
            const match = stdout.match(/Workflow created with ID: ([a-f0-9-]+)/);
            return match ? match[1] : null;
            
        } catch (error) {
            console.error('Failed to create workflow:', error);
            return null;
        }
    }

    private async executeWorkflow(workflowId: string): Promise<void> {
        try {
            this.outputChannel.show();
            this.outputChannel.appendLine(`Executing workflow: ${workflowId}`);
            
            // Show progress notification
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Executing Workflow',
                cancellable: true
            }, async (progress, token) => {
                return new Promise<void>((resolve, reject) => {
                    const process = exec(
                        `maahelper workflow-execute "${workflowId}"`,
                        { cwd: vscode.workspace.rootPath }
                    );

                    process.stdout?.on('data', (data) => {
                        this.outputChannel.appendLine(data.toString());
                    });

                    process.stderr?.on('data', (data) => {
                        this.outputChannel.appendLine(`Error: ${data.toString()}`);
                    });

                    process.on('close', (code) => {
                        if (code === 0) {
                            vscode.window.showInformationMessage('Workflow completed successfully!');
                            resolve();
                        } else {
                            vscode.window.showErrorMessage(`Workflow failed with code ${code}`);
                            reject(new Error(`Process exited with code ${code}`));
                        }
                    });

                    token.onCancellationRequested(() => {
                        process.kill();
                        reject(new Error('Workflow execution cancelled'));
                    });
                });
            });

        } catch (error) {
            vscode.window.showErrorMessage(`Failed to execute workflow: ${error}`);
        }
    }

    private async showWorkflowStatus(workflowId: string): Promise<void> {
        try {
            const { stdout } = await execAsync(
                `maahelper workflow-status "${workflowId}" --json`,
                { cwd: vscode.workspace.rootPath }
            );
            
            const status = JSON.parse(stdout);
            
            const panel = vscode.window.createWebviewPanel(
                'workflowStatus',
                `Workflow Status: ${workflowId}`,
                vscode.ViewColumn.Beside,
                { enableScripts: true }
            );

            panel.webview.html = this.getWorkflowStatusHtml(status);

        } catch (error) {
            vscode.window.showErrorMessage(`Failed to get workflow status: ${error}`);
        }
    }

    private async executeWorkflowAction(workflowId: string, action: string): Promise<void> {
        try {
            let command = '';
            
            switch (action) {
                case 'status':
                    await this.showWorkflowStatus(workflowId);
                    return;
                case 'execute':
                    await this.executeWorkflow(workflowId);
                    return;
                case 'pause':
                    command = `maahelper workflow-pause "${workflowId}"`;
                    break;
                case 'resume':
                    command = `maahelper workflow-resume "${workflowId}"`;
                    break;
                case 'cancel':
                    command = `maahelper workflow-cancel "${workflowId}"`;
                    break;
                case 'checkpoint':
                    const checkpointName = await vscode.window.showInputBox({
                        prompt: 'Enter checkpoint name',
                        placeHolder: 'checkpoint-name'
                    });
                    if (checkpointName) {
                        command = `maahelper workflow-checkpoint "${workflowId}" "${checkpointName}"`;
                    }
                    break;
                case 'list-checkpoints':
                    command = `maahelper workflow-checkpoints "${workflowId}"`;
                    break;
            }

            if (command) {
                const { stdout } = await execAsync(command, {
                    cwd: vscode.workspace.rootPath
                });
                
                vscode.window.showInformationMessage(stdout.trim());
            }

        } catch (error) {
            vscode.window.showErrorMessage(`Action failed: ${error}`);
        }
    }

    private async collectTemplateInputs(template: any): Promise<any> {
        const inputs: any = {};
        
        // Common inputs that might need collection
        const inputPrompts = {
            'feature_name': 'Feature name',
            'requirements': 'Feature requirements',
            'bug_description': 'Bug description',
            'project_name': 'Project name',
            'project_type': 'Project type',
            'license_type': 'License type'
        };

        for (const [key, prompt] of Object.entries(inputPrompts)) {
            if (template.default_inputs && key in template.default_inputs && !template.default_inputs[key]) {
                const value = await vscode.window.showInputBox({
                    prompt: prompt,
                    placeHolder: `Enter ${prompt.toLowerCase()}`
                });
                
                if (value) {
                    inputs[key] = value;
                }
            }
        }

        return inputs;
    }

    private getWorkflowStatusHtml(status: any): string {
        return `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Workflow Status</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: var(--vscode-foreground);
                    background-color: var(--vscode-editor-background);
                    padding: 20px;
                }
                .status-card {
                    background-color: var(--vscode-textBlockQuote-background);
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 15px;
                    border-left: 4px solid var(--vscode-textLink-foreground);
                }
                .progress-bar {
                    width: 100%;
                    height: 20px;
                    background-color: var(--vscode-progressBar-background);
                    border-radius: 10px;
                    overflow: hidden;
                    margin: 10px 0;
                }
                .progress-fill {
                    height: 100%;
                    background-color: var(--vscode-progressBar-foreground);
                    transition: width 0.3s ease;
                }
                .status-badge {
                    display: inline-block;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: bold;
                    text-transform: uppercase;
                }
                .status-running { background-color: #007acc; color: white; }
                .status-completed { background-color: #28a745; color: white; }
                .status-failed { background-color: #dc3545; color: white; }
                .status-paused { background-color: #ffc107; color: black; }
            </style>
        </head>
        <body>
            <h1>Workflow Status</h1>
            
            <div class="status-card">
                <h3>Overview</h3>
                <p><strong>ID:</strong> ${status.id}</p>
                <p><strong>Name:</strong> ${status.name || 'Unknown'}</p>
                <p><strong>Status:</strong> <span class="status-badge status-${status.status}">${status.status}</span></p>
                
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${status.progress_percentage || 0}%"></div>
                </div>
                <p><strong>Progress:</strong> ${status.completed_steps || 0}/${status.total_steps || 0} steps (${status.progress_percentage || 0}%)</p>
            </div>

            <div class="status-card">
                <h3>Step Details</h3>
                <p><strong>Completed Steps:</strong> ${status.completed_steps || 0}</p>
                <p><strong>Failed Steps:</strong> ${status.failed_steps || 0}</p>
                <p><strong>Running Steps:</strong> ${status.running_steps || 0}</p>
            </div>
        </body>
        </html>`;
    }
}
