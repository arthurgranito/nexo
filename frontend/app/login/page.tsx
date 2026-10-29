"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { signInWithGoogle } from "@/lib/auth";
import { getSupabase, supabaseConfigured } from "@/lib/supabase";
import { writeAccessToken } from "@/lib/session";

const devAuthEnabled = process.env.NEXT_PUBLIC_DEV_AUTH === "true";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "signup">("login");
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
        if (mode === "signup") {
          const { data, error: signError } = await supabase.auth.signUp({ email, password });
          if (signError) {
            throw new Error(signError.message);
          }
          if (!data.session) {
            throw new Error(
              "Conta criada. Confirme o e-mail no link enviado pelo Supabase e volte para entrar.",
            );
          }
          writeAccessToken(data.session.access_token);
        } else {
          const { data, error: signError } = await supabase.auth.signInWithPassword({
            email,
            password,
          });
          if (signError || !data.session) {
            throw new Error(signError?.message ?? "Credenciais inválidas.");
          }
          writeAccessToken(data.session.access_token);
        }
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

  async function onGoogle() {
    setError("");
    setBusy(true);
    try {
      const supabase = getSupabase();
      if (!supabase) {
        throw new Error("Configure NEXT_PUBLIC_SUPABASE_URL e NEXT_PUBLIC_SUPABASE_ANON_KEY.");
      }
      await signInWithGoogle(supabase);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Falha ao abrir login Google.");
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col justify-center p-6">
      <h1 className="mb-2 text-3xl font-semibold">Entrar no Nexo</h1>
      <p className="mb-8 text-sm text-slate-600">
        {supabaseReady
          ? "E-mail e senha ou Google (via Supabase). Nenhuma service role no navegador."
          : "Ambiente local: informe o token de desenvolvimento do .env."}
      </p>
      {supabaseReady && (
        <div className="mb-4 space-y-3">
          <Button
            type="button"
            className="w-full bg-white text-slate-800 ring-1 ring-slate-300 hover:bg-slate-50"
            disabled={busy}
            onClick={onGoogle}
          >
            Continuar com Google
          </Button>
          <p className="text-center text-xs text-slate-500">ou use e-mail e senha</p>
        </div>
      )}
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
                minLength={6}
                autoComplete={mode === "signup" ? "new-password" : "current-password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <Button className="w-full" disabled={busy}>
              {busy ? "Aguarde…" : mode === "signup" ? "Criar conta" : "Entrar com e-mail"}
            </Button>
            <button
              type="button"
              className="w-full text-sm text-emerald-700 underline"
              onClick={() => setMode(mode === "login" ? "signup" : "login")}
            >
              {mode === "login" ? "Não tem conta? Cadastre-se" : "Já tem conta? Entrar"}
            </button>
          </>
        ) : (
          <>
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
            <Button className="w-full" disabled={busy}>
              {busy ? "Entrando…" : "Entrar"}
            </Button>
          </>
        )}
      </form>
      {error && (
        <p role="alert" className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-800">
          {error}
        </p>
      )}
    </main>
  );
}
