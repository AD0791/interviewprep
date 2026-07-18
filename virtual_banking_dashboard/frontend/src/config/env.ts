import { z } from 'zod';

const envSchema = z.object({
  VITE_API_URL: z.string().url().default('http://localhost:8000/api'),
  VITE_APP_ENV: z.enum(['development', 'staging', 'production']).default('development'),
});

const parseResult = envSchema.safeParse(import.meta.env);

if (!parseResult.success) {
  console.error('❌ Frontend Env Variable Validation Error:');
  console.error(JSON.stringify(parseResult.error.format(), null, 2));
  throw new Error('Missing required environment keys inside Vite config compiling scope.');
}

export const env = parseResult.data;
