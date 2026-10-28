"use client";

import { FormEvent, useState } from "react";
import { Button } from "@/components/ui/button";
import { apiRequest } from "@/lib/api";
import { readCacheEpoch } from "@/lib/session";

type Source = { id: string; name: string; kind: string; status: string };
type Answer = { answer: string; status: string; message_id: string; trace: string[] };

export default function WorkspacePage() {
  const [question, setQuestion] = useState("");
  const [sources, setSources] = useState<Source[]>([]);
  const [name, setName] = useState("");
  const [kind, setKind] = useState("csv");
  const [answer, setAnswer] = useState<Answer | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const scopeKey = readCacheEpoch();

  async function run(fn: () => Promise<void>) {
    setError("");
    setBusy(true);
    try {
      await fn();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Falha de conexão");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto max-w-6xl p-5 md:p-10" key={scopeKey}>
      <section className="mb-10 max-w-2xl">
        <p className="mb-3 text-xs font-bold uppercase tracking-widest text-emerald-700">
          Inteligência conectada ao negócio
        </p>
        <h1 className="mb-4 text-4xl font-semibold leading-tight">
          Um lugar para conversar
          <br />
          com a sua empresa.
        </h1>
        <p className="text-slate-600">
          Cadastre fontes e prepare o contexto do assistente. O motor analítico será conectado nas
          próximas fases do roadmap.
        </p>
      </section>
      <div className="grid gap-6 md:grid-cols-[300px_1fr]">
        <aside className="space-y-4 rounded-2xl border bg-white p-6">
          <h2 className="text-lg font-semibold">Fontes</h2>
          <Button disabled={busy} onClick={() => run(async () => setSources(await apiRequest("/v1/sources")))}>
            Carregar fontes
          </Button>
          <div className="border-t pt-4">
            {sources.length === 0 ? (
              <p className="text-sm text-slate-500">Nenhuma fonte carregada.</p>
            ) : (
              sources.map((source) => (
                <div key={source.id} className="mb-3 rounded-lg bg-slate-50 p-3 text-sm">
                  <strong>{source.name}</strong>
                  <p>
                    {source.kind} · {source.status}
                  </p>
                </div>
              ))
            )}
          </div>
        </aside>
        <div className="space-y-6">
          <section className="rounded-2xl border bg-white p-6">
            <h2 className="mb-4 text-lg font-semibold">Adicionar uma fonte</h2>
            <form
              className="flex flex-wrap gap-3"
              onSubmit={(event: FormEvent) => {
                event.preventDefault();
                run(async () => {
                  await apiRequest("/v1/sources", { method: "POST", body: { name, kind } });
                  setName("");
                  setSources(await apiRequest("/v1/sources"));
                });
              }}
            >
              <div className="min-w-40 flex-1">
                <label htmlFor="name">Nome</label>
                <input
                  id="name"
                  required
                  minLength={2}
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Vendas da loja"
                />
              </div>
              <div className="w-40">
                <label htmlFor="kind">Tipo</label>
                <select id="kind" value={kind} onChange={(e) => setKind(e.target.value)}>
                  {["csv", "xlsx", "google_sheets", "postgres", "mysql"].map((item) => (
                    <option key={item}>{item}</option>
                  ))}
                </select>
              </div>
              <Button className="self-end" disabled={busy}>
                Cadastrar
              </Button>
            </form>
          </section>
          <section className="rounded-2xl border bg-white p-6">
            <h2 className="mb-4 text-lg font-semibold">Conversa</h2>
            <form
              onSubmit={(event: FormEvent) => {
                event.preventDefault();
                run(async () => setAnswer(await apiRequest("/v1/chat", { body: { text: question } })));
              }}
            >
              <label htmlFor="question">O que você quer entender?</label>
              <textarea
                id="question"
                required
                minLength={3}
                rows={3}
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Qual loja vendeu mais neste mês?"
              />
              <Button className="mt-3" disabled={busy}>
                {busy ? "Processando…" : "Enviar pergunta"}
              </Button>
            </form>
            {answer && (
              <div className="mt-5 rounded-xl bg-emerald-50 p-5" aria-live="polite">
                <p>{answer.answer}</p>
                <p className="mt-3 text-xs text-slate-500">
                  {answer.status} · {answer.trace.join(" → ")}
                </p>
              </div>
            )}
          </section>
        </div>
      </div>
      {error && (
        <p role="alert" className="mt-5 rounded-lg bg-red-50 p-4 text-red-800">
          {error}
        </p>
      )}
    </main>
  );
}
