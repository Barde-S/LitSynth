import { ChatMessage, Chat } from '../types';
import { format } from 'date-fns';

export type ExportFormat = 'json' | 'markdown' | 'txt' | 'pdf';

export class ExportService {
  /**
   * Export chat history in specified format
   */
  static async exportChat(
    chat: Chat,
    messages: ChatMessage[],
    exportFormat: ExportFormat,
    workspaceName?: string
  ): Promise<void> {
    switch (exportFormat) {
      case 'json':
        return this.exportJSON(chat, messages, workspaceName);
      case 'markdown':
        return this.exportMarkdown(chat, messages, workspaceName);
      case 'txt':
        return this.exportTXT(chat, messages, workspaceName);
      case 'pdf':
        return this.exportPDF(chat, messages, workspaceName);
      default:
        throw new Error(`Unsupported format: ${exportFormat}`);
    }
  }

  /**
   * Export as JSON with full metadata
   */
  private static exportJSON(chat: Chat, messages: ChatMessage[], workspaceName?: string): void {
    const data = {
      metadata: {
        workspace: workspaceName,
        chat_title: chat.title,
        chat_id: chat.chat_id,
        created_at: chat.created_at,
        updated_at: chat.updated_at,
        message_count: chat.message_count,
        exported_at: new Date().toISOString(),
        export_version: '1.0'
      },
      messages: messages.map(msg => ({
        id: msg.id,
        role: msg.role,
        content: msg.content,
        timestamp: msg.timestamp,
        sources: msg.sources || []
      }))
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    this.downloadFile(blob, `${this.sanitizeFilename(chat.title)}.json`);
  }

  /**
   * Export as Markdown with formatting
   */
  private static exportMarkdown(chat: Chat, messages: ChatMessage[], workspaceName?: string): void {
    let markdown = `# ${chat.title}\n\n`;

    if (workspaceName) {
      markdown += `**Workspace:** ${workspaceName}\n`;
    }
    markdown += `**Created:** ${format(new Date(chat.created_at), 'PPpp')}\n`;
    markdown += `**Last Updated:** ${format(new Date(chat.updated_at), 'PPpp')}\n`;
    markdown += `**Messages:** ${chat.message_count}\n\n`;
    markdown += `---\n\n`;

    messages.forEach((msg) => {
      const timestamp = format(new Date(msg.timestamp), 'PPpp');
      const role = msg.role === 'user' ? 'You' : 'LitSynth';

      markdown += `## ${role} - ${timestamp}\n\n`;
      markdown += `${msg.content}\n\n`;

      // Add sources if present
      if (msg.sources && msg.sources.length > 0) {
        markdown += `**Sources:**\n`;
        msg.sources.forEach(source => {
          markdown += `- [p.${source.page}, ${source.source}] ${source.snippet}\n`;
        });
        markdown += `\n`;
      }

      markdown += `---\n\n`;
    });

    const blob = new Blob([markdown], { type: 'text/markdown' });
    this.downloadFile(blob, `${this.sanitizeFilename(chat.title)}.md`);
  }

  /**
   * Export as plain text
   */
  private static exportTXT(chat: Chat, messages: ChatMessage[], workspaceName?: string): void {
    let text = `${chat.title}\n`;
    text += `${'='.repeat(chat.title.length)}\n\n`;

    if (workspaceName) {
      text += `Workspace: ${workspaceName}\n`;
    }
    text += `Created: ${format(new Date(chat.created_at), 'PPpp')}\n`;
    text += `Last Updated: ${format(new Date(chat.updated_at), 'PPpp')}\n`;
    text += `Messages: ${chat.message_count}\n\n`;
    text += `${'-'.repeat(80)}\n\n`;

    messages.forEach((msg) => {
      const timestamp = format(new Date(msg.timestamp), 'PPpp');
      const role = msg.role === 'user' ? 'YOU' : 'LITSYNTH';

      text += `[${timestamp}] ${role}:\n`;
      text += `${msg.content}\n`;

      if (msg.sources && msg.sources.length > 0) {
        text += `\nSources:\n`;
        msg.sources.forEach(source => {
          text += `  - [p.${source.page}, ${source.source}]\n`;
        });
      }

      text += `\n${'-'.repeat(80)}\n\n`;
    });

    const blob = new Blob([text], { type: 'text/plain' });
    this.downloadFile(blob, `${this.sanitizeFilename(chat.title)}.txt`);
  }

  /**
   * Export as PDF (browser print dialog)
   */
  private static async exportPDF(chat: Chat, messages: ChatMessage[], workspaceName?: string): Promise<void> {
    // Create a new window with formatted HTML
    const printWindow = window.open('', '', 'width=800,height=600');
    if (!printWindow) {
      throw new Error('Popup blocked. Please allow popups for PDF export.');
    }

    // Generate HTML content
    let html = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>${chat.title}</title>
        <style>
          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            line-height: 1.6;
            color: #333;
          }
          h1 {
            border-bottom: 3px solid #333;
            padding-bottom: 10px;
          }
          .metadata {
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
          }
          .message {
            margin-bottom: 30px;
            page-break-inside: avoid;
          }
          .message-header {
            font-weight: bold;
            color: #444;
            margin-bottom: 10px;
            font-size: 14px;
          }
          .user { color: #2563eb; }
          .assistant { color: #059669; }
          .message-content {
            background: #f9fafb;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #e5e7eb;
          }
          .sources {
            margin-top: 10px;
            padding: 10px;
            background: #fef3c7;
            border-radius: 4px;
            font-size: 12px;
          }
          .sources-title {
            font-weight: bold;
            margin-bottom: 5px;
          }
          @media print {
            body { padding: 20px; }
          }
        </style>
      </head>
      <body>
        <h1>${this.escapeHtml(chat.title)}</h1>
        <div class="metadata">
          ${workspaceName ? `<div><strong>Workspace:</strong> ${this.escapeHtml(workspaceName)}</div>` : ''}
          <div><strong>Created:</strong> ${format(new Date(chat.created_at), 'PPpp')}</div>
          <div><strong>Last Updated:</strong> ${format(new Date(chat.updated_at), 'PPpp')}</div>
          <div><strong>Messages:</strong> ${chat.message_count}</div>
        </div>
    `;

    messages.forEach(msg => {
      const timestamp = format(new Date(msg.timestamp), 'PPpp');
      const roleClass = msg.role === 'user' ? 'user' : 'assistant';
      const roleName = msg.role === 'user' ? 'You' : 'LitSynth';

      html += `
        <div class="message">
          <div class="message-header ${roleClass}">
            ${roleName} - ${timestamp}
          </div>
          <div class="message-content">
            ${this.escapeHtml(msg.content).replace(/\n/g, '<br>')}
          </div>
      `;

      if (msg.sources && msg.sources.length > 0) {
        html += `
          <div class="sources">
            <div class="sources-title">Sources:</div>
            <ul style="margin: 5px 0; padding-left: 20px;">
        `;
        msg.sources.forEach(source => {
          html += `<li>[p.${source.page}, ${this.escapeHtml(source.source)}]</li>`;
        });
        html += `</ul></div>`;
      }

      html += `</div>`;
    });

    html += `
      </body>
      </html>
    `;

    printWindow.document.write(html);
    printWindow.document.close();

    // Wait for content to load, then trigger print
    printWindow.onload = () => {
      printWindow.print();
      // Don't auto-close - let user close after printing
    };
  }

  /**
   * Escape HTML to prevent XSS
   */
  private static escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * Sanitize filename for download
   */
  private static sanitizeFilename(filename: string): string {
    return filename
      .replace(/[^a-z0-9]/gi, '_')
      .replace(/_+/g, '_')
      .toLowerCase()
      .substring(0, 50);
  }

  /**
   * Trigger file download
   */
  private static downloadFile(blob: Blob, filename: string): void {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }
}
