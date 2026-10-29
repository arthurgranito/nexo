"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { persistSupabaseSession } from "@/lib/auth";
import { getSupabase } from "@/lib/supabase";

function CallbackInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [message, setMessage] = useState("Conectando…");

  useEffect(() => {
    let active = true;
    async function finish() {
      const supabase = getSupabase();
      if (!supabase) {
        router.replace("/login");
        return;
      }
      const code = searchParams.get("code");
      if (code) {
        const { error } = await supabase.auth.exchangeCodeForSession(code);
        if (error) {
          if (active) {
            setMessage("Não foi possível concluir o login com Google.");
          }
          router.replace("/login");
          return;
        }
      }
      const ok = await persistSupabaseSession(supabase);
      if (!active) {
        return;
      }
      if (ok) {
        router.replace("/app");
      } else {
        setMessage("Sessão não encontrada.");
        router.replace("/login");
      }
    }
    finish();
    return () => {
      active = false;
    };
  }, [router, searchParams]);

  return (
    <main className="mx-auto flex min-h-screen max-w-md items-center justify-center p-6 text-sm text-slate-600">
      {message}
    </main>
  );
}

export default function AuthCallbackPage() {
  return (
    <Suspense
      fallback={
        <main className="mx-auto flex min-h-screen max-w-md items-center justify-center p-6 text-sm text-slate-600">
          Conectando…
        </main>
      }
    >
      <CallbackInner />
    </Suspense>
  );
}
