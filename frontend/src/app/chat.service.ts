import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ChatPayload {
  session_id: string;
  message: string;
  intent: string;
  file_path?: string;
  cibil_score?: number;
  monthly_income?: number;
  existing_emi?: number;
}

@Injectable({ providedIn: 'root' })
export class ChatService {
  private baseUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  uploadFile(file: File): Observable<any> {
    const form = new FormData();
    form.append('file', file);
    return this.http.post(`${this.baseUrl}/upload`, form);
  }

  sendMessage(payload: ChatPayload): Observable<any> {
    const form = new FormData();
    Object.entries(payload).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        form.append(key, String(value));
      }
    });
    return this.http.post(`${this.baseUrl}/chat`, form);
  }
}


