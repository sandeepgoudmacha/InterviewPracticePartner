"""TypeScript types and interfaces."""
export interface User {
  id: string;
  email: string;
  name: string;
  resumeData?: Record<string, any>;
  createdAt: string;
}

export interface Interview {
  id: string;
  userId: string;
  type: "coding" | "hr" | "sales" | "memory";
  role: string;
  startedAt: string;
  endedAt?: string;
  score?: number;
  feedback?: Record<string, any>;
}

export interface InterviewResponse {
  question: string;
  answer: string;
  timestamp: string;
}
