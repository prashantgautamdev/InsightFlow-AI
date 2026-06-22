import { useState, useEffect, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import { Send, MessagesSquare, Loader2, Code2 } from "lucide-react";
import toast from "react-hot-toast";
import { api } from "@/api/client";

interface DatasetItem { id: string; file_name: string; status: string }
interface Message { role: "user" | "assistant"; content: string }

const SUGGESTED_QUESTIONS = [
  "Which feature has the highest correlation?",
  "Suggest the best model for this data.",
  "Which features should I remove?",
  "Show top 10 correlated columns.",
];

export default function ChatAssistantPage() {
  const [datasetId, setDatasetId] = useState<string>("");
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const { data: datasets } = useQuery<DatasetItem[]>({
    queryKey: ["datasets"],
    queryFn: async () => (await api.get("/datasets")).data,
  });

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage(text: string) {
    if (!text.trim()) return;
    setMessages((m) => [...m, { role: "user", content: text }]);
    setInput("");
    setSending(true);
    try {
      const { data } = await api.post("/chat/message", {
        session_id: sessionId,
        dataset_id: datasetId || undefined,
        message: text,
      });
      setSessionId(data.session_id);
      setMessages((m) => [...m, { role: "assistant", content: data.content }]);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? "Chat failed");
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="space-y-6 max-w-4xl h-full flex flex-col">
      <div>
        <h1 className="text-2xl font-bold mb-1">AI Dataset Chat Assistant</h1>
        <p className="text-muted text-sm">Ask questions about your data in plain English (RAG-powered).</p>
      </div>

      <div className="glass-card p-4">
        <label className="label-text">Active dataset (optional but recommended)</label>
        <select value={datasetId} onChange={(e) => { setDatasetId(e.target.value); setSessionId(undefined); setMessages([]); }} className="input-field max-w-md">
          <option value="">— General chat (no dataset context) —</option>
          {datasets?.filter((d) => d.status === "completed").map((d) => (
            <option key={d.id} value={d.id}>{d.file_name}</option>
          ))}
        </select>
      </div>

      <div className="glass-card flex-1 flex flex-col min-h-[420px] p-0 overflow-hidden">
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-muted py-10">
              <MessagesSquare className="mx-auto mb-3 opacity-40" size={32} />
              <p className="text-sm mb-4">Try asking:</p>
              <div className="flex flex-wrap gap-2 justify-center">
                {SUGGESTED_QUESTIONS.map((q) => (
                  <button key={q} onClick={() => sendMessage(q)}
                    className="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-xs transition-colors">
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm whitespace-pre-wrap ${
                m.role === "user" ? "bg-gradient-hero" : "bg-white/5 border border-border"
              }`}>
                {m.content}
              </div>
            </div>
          ))}
          {sending && (
            <div className="flex justify-start">
              <div className="rounded-2xl px-4 py-2.5 bg-white/5 border border-border">
                <Loader2 className="animate-spin text-primary-light" size={16} />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <form
          onSubmit={(e) => { e.preventDefault(); sendMessage(input); }}
          className="flex items-center gap-2 border-t border-border p-3"
        >
          <Code2 className="text-muted shrink-0" size={18} />
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your dataset..."
            className="input-field flex-1"
            disabled={sending}
          />
          <button type="submit" disabled={sending} className="btn-primary !px-4 !py-2.5">
            <Send size={16} />
          </button>
        </form>
      </div>
    </div>
  );
}
