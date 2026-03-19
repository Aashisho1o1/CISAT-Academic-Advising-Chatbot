import { create } from 'zustand';

interface AdvisingState {
  threadId: string | null;
  fileId: string | null;
  extractedData: Record<string, any> | null;
  setSession: (threadId: string, fileId: string) => void;
  setExtractedData: (data: Record<string, any>) => void;
  clearSession: () => void;
}

export const useAdvisingStore = create<AdvisingState>((set) => ({
  threadId: null,
  fileId: null,
  extractedData: null,
  setSession: (threadId, fileId) => set({ threadId, fileId }),
  setExtractedData: (data) => set({ extractedData: data }),
  clearSession: () => set({ threadId: null, fileId: null, extractedData: null }),
}));
