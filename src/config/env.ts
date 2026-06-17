type EnvConfig = {
  baseUrl: string;
  apiBaseUrl: string;
  customerEmail: string;
  customerPassword: string;
  headless: boolean;
  defaultTimeoutMs: number;
  allowKnownDefects: boolean;
};

const boolFromEnv = (value: string | undefined, fallback: boolean): boolean => {
  if (value === undefined) return fallback;
  return ['1', 'true', 'yes', 'y', 'on'].includes(value.toLowerCase());
};

const numberFromEnv = (value: string | undefined, fallback: number): number => {
  if (!value) return fallback;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
};

const normalizeUrl = (url: string): string => (url.endsWith('/') ? url : `${url}/`);

export const envConfig: EnvConfig = {
  baseUrl: normalizeUrl(process.env.BASE_URL ?? 'https://staging-app.webvio.in/'),
  apiBaseUrl: normalizeUrl(process.env.API_BASE_URL ?? 'https://staging-api.angelecho.ai/v1/'),
  customerEmail: process.env.CUSTOMER_EMAIL ?? 'new_customer@yopmail.com',
  customerPassword: process.env.CUSTOMER_PASSWORD ?? 'Test@123',
  headless: boolFromEnv(process.env.HEADLESS, true),
  defaultTimeoutMs: numberFromEnv(process.env.DEFAULT_TIMEOUT_MS, 15_000),
  allowKnownDefects: boolFromEnv(process.env.ALLOW_KNOWN_DEFECTS, true)
};
