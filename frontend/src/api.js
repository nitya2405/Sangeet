// Central API base URL — reads VITE_API_URL at build time.
// In dev: empty string (Vite proxy handles /api → localhost:8000)
// In production: set VITE_API_URL=https://your-space.hf.space in Vercel env vars
export const API_BASE = import.meta.env.VITE_API_URL ?? ''

export function wsUrl(path) {
  const base = API_BASE
    ? API_BASE.replace(/^http/, 'ws')
    : `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}`
  return `${base}${path}`
}
