"use client";

import { useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiPost } from "@/lib/api";
import type { Lang } from "@/lib/i18n";

type BotReply = { ok: boolean; reply?: string; delivered?: boolean; mode?: "real" | "demo" };
type Bubble = { from: "citizen" | "bot"; text: string };

/**
 * Messaging-bot channel in the browser: posts Telegram-format updates to the same webhook the
 * Telegram bot uses (POST /api/webhooks/messaging) and shows the bot's replies as a chat.
 */
export function ChatBot({ state, lang, t }: {
  state: string;
  lang: Lang;
  t: { chatHint: string; chatPlaceholder: string; chatSend: string; sending: string };
}) {
  const chatId = useRef<number>(0);
  const sentState = useRef<string | null>(null);
  const [bubbles, setBubbles] = useState<Bubble[]>([]);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [mode, setMode] = useState<"real" | "demo" | null>(null);

  async function post(message: string): Promise<BotReply> {
    if (!chatId.current) chatId.current = Math.floor(Math.random() * 1e9) + 1;
    return apiPost<BotReply>("/api/webhooks/messaging", { message: { chat: { id: chatId.current }, text: message } });
  }

  async function send() {
    const msg = text.trim();
    if (!msg || busy) return;
    setBusy(true);
    setText("");
    setBubbles((b) => [...b, { from: "citizen", text: msg }]);
    try {
      if (sentState.current !== state) {
        await post(`/state ${state}`); // the bot needs to know the citizen's state, like /state on Telegram
        sentState.current = state;
      }
      const r = await post(msg);
      setMode(r.mode ?? null);
      setBubbles((b) => [...b, { from: "bot", text: r.reply ?? "…" }]);
    } catch (e) {
      setBubbles((b) => [...b, { from: "bot", text: e instanceof Error ? e.message : String(e) }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex flex-col gap-3">
      <p className="text-sm text-muted-foreground">
        {t.chatHint}
        {mode === "demo" && (
          <span className="mt-1 block text-xs text-amber-800">
            Demo mode: TELEGRAM_BOT_TOKEN is not set, so replies are shown here instead of being sent on Telegram.
          </span>
        )}
      </p>
      {bubbles.length > 0 && (
        <div className="flex max-h-80 flex-col gap-2 overflow-y-auto rounded-lg border bg-muted/30 p-3">
          {bubbles.map((b, i) => (
            <div
              key={i}
              lang={b.from === "citizen" ? lang : undefined}
              className={
                b.from === "citizen"
                  ? "max-w-[85%] self-end rounded-2xl rounded-br-sm bg-primary px-3 py-2 text-sm text-primary-foreground"
                  : "max-w-[85%] self-start rounded-2xl rounded-bl-sm border bg-background px-3 py-2 text-sm"
              }
            >
              {b.text}
            </div>
          ))}
          {busy && <div className="self-start text-xs text-muted-foreground">{t.sending}</div>}
        </div>
      )}
      <form
        className="flex gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          void send();
        }}
      >
        <Input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={t.chatPlaceholder}
          lang={lang}
          className="h-10 text-base"
        />
        <Button type="submit" disabled={busy || text.trim().length < 1}>
          {t.chatSend}
        </Button>
      </form>
    </div>
  );
}
