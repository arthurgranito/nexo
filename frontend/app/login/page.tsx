"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { getSupabase, supabaseConfigured } from "@/lib/supabase";
import { writeAccessToken } from "@/lib/session";

const devAuthEnabled = process.env.NEXT_PUBLIC_DEV_AUTH === "true";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [devToken, setDevToken] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const supabaseReady = supabaseConfigured();

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setBusy(true);
    try {
      const supabase = getSupabase();
      if (supabase) {
        const { data, error: signError } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (signError || !data.session) {
          throw new Error(signError?.message ?? "Credenciais inválidas.");
        }
        writeAccessToken(data.session.access_token);
      } else if (devAuthEnabled) {
        if (devToken.length < 24) {
          throw new Error("Informe o token local com pelo menos 24 caracteres.");
        }
        writeAccessToken(devToken);
      } else {
        throw new Error("Configure Supabase ou habilite auth de desenvolvimento.");
      }
      router.replace("/app");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Falha ao entrar.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col justify-center p-6">
      <h1 className="mb-2 text-3xl font-semibold">Entrar no Nexo</h1>
      <p className="mb-8 text-sm text-slate-600">
        {supabaseReady
          ? "Use sua conta Supabase. Nenhuma service role é usada no navegador."
          : "Ambiente local: informe o token de desenvolvimento do .env."}
      </p>
      <form className="space-y-4 rounded-2xl border bg-white p-6" onSubmit={onSubmit}>
        {supabaseReady ? (
          <>
            <div>
              <label htmlFor="email">E-mail</label>
              <input
                id="email"
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="password">Senha</label>
              <input
                id="password"
                type="password"
                required
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </>
        ) : (
          <div>
            <label htmlFor="dev-token">Token local (DEV_TOKEN)</label>
            <input
              id="dev-token"
              type="password"
              required
              minLength={24}
              autoComplete="off"
              value={devToken}
              onChange={(e) => setDevToken(e.target.value)}
            />
          </div>
        )}
        <Button className="w-full" disabled={busy}>
          {busy ? "Entrando…" : "Entrar"}
        </Button>
      </form>
      {error && (
        <p role="alert" className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-800">
          {error}
        </p>
      )}
    </main>
  );
}
