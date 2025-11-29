import { Component } from '@angular/core';
import { ChatService } from '../chat.service';

type Intent = 'spending_plan' | 'tax_saver' | 'investment' | 'loan';

interface ChatBubble {
  role: 'user' | 'assistant';
  content: string;
}

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss'],
})
export class ChatComponent {
  sessionId = crypto.randomUUID();
  intent: Intent = 'spending_plan';
  cibilScore?: number;
  monthlyIncome?: number;
  existingEmi?: number;
  filePath?: string;

  messages: ChatBubble[] = [];
  input = '';
  uploading = false;
  sending = false;

  spendingData?: Record<string, number>;

  constructor(private chatService: ChatService) {}

  private typeOut(text: string, target: ChatBubble, done: () => void): void {
    const chars = Array.from(text);
    let index = 0;
    const interval = setInterval(() => {
      target.content += chars[index] ?? '';
      index += 1;
      if (index >= chars.length) {
        clearInterval(interval);
        done();
      }
    }, 15);
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;
    this.uploading = true;
    this.chatService.uploadFile(file).subscribe({
      next: (res) => {
        this.filePath = res.path;
        this.uploading = false;
      },
      error: () => {
        this.uploading = false;
        this.messages.push({
          role: 'assistant',
          content: 'Upload failed. Please try again.',
        });
      },
    });
  }

  send(): void {
    if (!this.input.trim()) return;
    const userMsg = this.input.trim();
    this.messages.push({ role: 'user', content: userMsg });
    this.sending = true;

    // Optimistically create an empty assistant bubble we will "type into"
    const assistantBubble: ChatBubble = { role: 'assistant', content: '' };
    this.messages.push(assistantBubble);

    this.chatService
      .sendMessage({
        session_id: this.sessionId,
        message: userMsg,
        intent: this.intent,
        file_path: this.filePath,
        cibil_score: this.intent === 'loan' ? this.cibilScore : undefined,
        monthly_income:
          this.intent === 'loan' ? this.monthlyIncome : undefined,
        existing_emi: this.intent === 'loan' ? this.existingEmi : undefined,
      })
      .subscribe({
        next: (res) => {
          const assistantMsg: string = res.summary ?? 'No response';
          this.typeOut(assistantMsg, assistantBubble, () => {
            this.sending = false;
          });
          if (this.intent === 'spending_plan' && res.data?.category_percent) {
            this.spendingData = res.data.category_percent;
          }
        },
        error: () => {
          assistantBubble.content =
            'Error connecting to Spendly backend. Please try again.';
          this.sending = false;
        },
      });

    this.input = '';
  }
}


