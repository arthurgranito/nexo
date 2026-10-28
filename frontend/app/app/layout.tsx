"use client";

import { ReactNode, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { fetchOrganizations, type Organization } from "@/lib/api";
import { getSupabase } from "@/lib/supabase";
import {
  clearSession,
  readAccessToken,
  readCacheEpoch,
  readTenantId,
  writeAccessToken,
  writeTenantId,
} from "@/lib/session";

export default function AppShell({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [tenantId, setTenantId] = useState("");
  const [ready, setReady] = useState(false);
  const [error, setError] = useState("");
  const cacheEpoch = readCacheEpoch();

  useEffect(() => {
    let active = true;
    async function boot() {
      setError("");
      try {
        const supabase = getSupabase();
        if (supabase) {
          const { data } = await supabase.auth.getSession();
          if (!data.session) {
            router.replace("/login");
            return;
          }
          writeAccessToken(data.session.access_token);
          const { data: refreshed } = await supabase.auth.refreshSession();
          if (refreshed.session) {
            writeAccessToken(refreshed.session.access_token);
          }
        } else if (!readAccessToken()) {
          router.replace("/login");
          return;
        }
        const items = await fetchOrganizations();
        if (!items.length) {
          throw new Error("Nenhuma organização disponível para este usuário.");
        }
        const stored = readTenantId();
        const selected = items.some((item) => item.id === stored) ? stored : items[0].id;
        writeTenantId(selected);
        if (active) {
          setOrganizations(items);
          setTenantId(selected);
          setReady(true);
        }
      } catch (e) {
        if (active) {
          setError(e instanceof Error ? e.message : "Falha ao carregar sessão.");
        }
      }
    }
    boot();
    return () => {
      active = false;
    };
  }, [router, cacheEpoch]);

  async function logout() {
    const supabase = getSupabase();
    if (supabase) {
      await supabase.auth.signOut();
    }
    clearSession();
    router.replace("/login");
  }

  function changeTenant(nextTenant: string) {
    writeTenantId(nextTenant);
    setTenantId(nextTenant);
  }

  if (!ready) {
    return (
      <main className="mx-auto max-w-6xl p-8 text-sm text-slate-600">
        {error || "Carregando sessão…"}
      </main>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 p-4">
          <div className="text-xl font-bold">
            nexo<span className="text-emerald-600">.</span>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <label className="text-sm text-slate-600" htmlFor="org">
              Organização
            </label>
            <select
              id="org"
              className="rounded-lg border px-3 py-2 text-sm"
              value={tenantId}
              onChange={(e) => changeTenant(e.target.value)}
            >
              {organizations.map((org) => (
                <option key={org.id} value={org.id}>
                  {org.id.slice(0, 8)}… ({org.role})
                </option>
              ))}
            </select>
            <Button className="bg-white text-emerald-800 ring-1 ring-emerald-200" onClick={logout}>
              Sair
            </Button>
          </div>
        </div>
      </header>
      <div key={`${tenantId}-${cacheEpoch}`}>{children}</div>
    </div>
  );
}
