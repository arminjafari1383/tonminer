import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

function envValue(name) {
  if (process.env[name]) return process.env[name];
  for (const file of ['.env.production.local', '.env.production', '.env.local', '.env']) {
    try {
      const line = readFileSync(resolve(process.cwd(), file), 'utf8')
        .split(/\r?\n/)
        .find((entry) => entry.trim().startsWith(`${name}=`));
      if (line) return line.slice(line.indexOf('=') + 1).trim().replace(/^['"]|['"]$/g, '');
    } catch { /* optional env file */ }
  }
  return '';
}

const configured = envValue('VITE_PUBLIC_URL').replace(/\/+$/, '');
const isProductionBuild = process.env.npm_lifecycle_event === 'prebuild';
const appUrl = configured || (isProductionBuild ? '' : 'http://localhost:5173');

if (!appUrl || (isProductionBuild && !/^https:\/\//i.test(appUrl))) {
  throw new Error('Set VITE_PUBLIC_URL to the public HTTPS origin in .env before building the production frontend.');
}

const manifest = { url: appUrl, name: 'TON Miner', iconUrl: `${appUrl}/icon.png` };
writeFileSync(new URL('../public/tonconnect-manifest.json', import.meta.url), `${JSON.stringify(manifest, null, 2)}\n`);
console.log(`TON Connect manifest generated for ${appUrl}`);
