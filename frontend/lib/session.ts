const TOKEN_KEY = "nexo.access_token";
const TENANT_KEY = "nexo.tenant_id";
const CACHE_KEY = "nexo.cache_epoch";

export function readAccessToken(): string {
  if (typeof window === "undefined") {
    return "";
  }
  return sessionStorage.getItem(TOKEN_KEY) ?? "";
}

export function writeAccessToken(token: string): void {
  sessionStorage.setItem(TOKEN_KEY, token);
}

export function clearAccessToken(): void {
  sessionStorage.removeItem(TOKEN_KEY);
}

export function readTenantId(): string {
  if (typeof window === "undefined") {
    return "";
  }
  return localStorage.getItem(TENANT_KEY) ?? "";
}

export function writeTenantId(tenantId: string): void {
  localStorage.setItem(TENANT_KEY, tenantId);
  bumpCacheEpoch();
}

export function bumpCacheEpoch(): void {
  localStorage.setItem(CACHE_KEY, String(Date.now()));
}

export function readCacheEpoch(): string {
  if (typeof window === "undefined") {
    return "0";
  }
  return localStorage.getItem(CACHE_KEY) ?? "0";
}

export function clearSession(): void {
  clearAccessToken();
  localStorage.removeItem(TENANT_KEY);
  bumpCacheEpoch();
}
