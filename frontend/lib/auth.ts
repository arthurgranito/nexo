import type { SupabaseClient } from "@supabase/supabase-js";

import { writeAccessToken } from "@/lib/session";

export function oauthRedirectUrl(): string {
  if (typeof window !== "undefined") {
    return `${window.location.origin}/auth/callback`;
  }
  const site = process.env.NEXT_PUBLIC_SITE_URL?.replace(/\/$/, "");
  return site ? `${site}/auth/callback` : "http://localhost:3000/auth/callback";
}

export async function persistSupabaseSession(supabase: SupabaseClient): Promise<boolean> {
  const { data, error } = await supabase.auth.getSession();
  if (error || !data.session) {
    return false;
  }
  writeAccessToken(data.session.access_token);
  return true;
}

export async function signInWithGoogle(supabase: SupabaseClient): Promise<void> {
  const { error } = await supabase.auth.signInWithOAuth({
    provider: "google",
    options: {
      redirectTo: oauthRedirectUrl(),
      queryParams: { prompt: "select_account" },
    },
  });
  if (error) {
    throw new Error(error.message);
  }
}
