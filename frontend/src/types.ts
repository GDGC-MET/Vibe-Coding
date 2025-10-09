export type Settings = {
  personalities: string[];
  providers: string[];
  current: {
    personality: string;
    provider: string;
    memory: boolean;
  };
};

export type ChatResponse = {
  reply: string;
};

export type ApiError = { error: string };
