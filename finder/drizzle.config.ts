import { defineConfig } from 'drizzle-kit';
export default defineConfig({
  out: './drizzle',
  dialect: 'sqlite',
  schema: './src/lib/schema.ts',
  dbCredentials: {
    url: 'file:../products.db',
  },
});
