import { readAccessToken, readTenantId } from "@/lib/session";

const API = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

export async function apiRequest<T>(
  path: string,
  options: { method?: string; body?: unknown; tenantId?: string; token?: string } = {},
): Promise<T> {
  const token = options.token ?? readAccessToken();
  const tenantId = options.tenantId ?? readTenantId();
  if (!token) {
    throw new Error("Sessão expirada. Faça login novamente.");
  }
  if (!tenantId) {
    throw new Error("Selecione uma organização.");
  }
  const response = await fetch(`${API}${path}`, {
    method: options.method ?? (options.body ? "POST" : "GET"),
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      "X-Tenant-ID": tenantId,
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
  });
  const data = await response.json();
  if (!response.ok) {
    const detail = data.error?.detail;
    throw new Error(typeof detail === "string" ? detail : "Não foi possível completar a operação.");
  }
  return data as T;
}

export type Organization = { id: string; role: string };

export async function fetchOrganizations(token?: string): Promise<Organization[]> {
  const access = token ?? readAccessToken();
  const response = await fetch(`${API}/v1/me/organizations`, {
    headers: { Authorization: `Bearer ${access}` },
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error("Não foi possível carregar suas organizações.");
  }
  return data.items as Organization[];
}
