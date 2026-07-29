import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";

const API = "http://localhost:8000";

const intentConfig = {
  SESSION_COACH: { label: "Session Coach", icon: "🏋️", color: "#b8f724" },
  NUTRITION: { label: "Nutrition Coach", icon: "🥗", color: "#4ade80" },
  PROGRESS: { label: "Progress Analysis", icon: "📈", color: "#a78bfa" },
  PLANNER: { label: "Weekly Planner", icon: "📅", color: "#f0a500" },
  GENERAL: { label: "Coach", icon: "💬", color: "#60a5fa" },
};

const suggestions = [
  { text: "Pull day - lat pulldown, rows, bicep curls", icon: "🏋️" },
  { text: "Had chicken rice bowl for lunch", icon: "🥗" },
  { text: "How am I doing this week?", icon: "📈" },
  { text: "Plan my workouts for next week", icon: "📅" },
];

function TypingIndicator() {
  return (
    <div style={{ display: "flex", alignItems: "flex-start", gap: 10, marginBottom: 16 }}>
      <div style={{ width: 32, height: 32, borderRadius: 10, background: "#1a2400", border: "1px solid #2d3d00", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14, flexShrink: 0 }}>💪</div>
      <div style={{ background: "#1a1a1a", border: "1px solid #2a2a32", borderRadius: "4px 12px 12px 12px", padding: "12px 16px", display: "flex", gap: 5, alignItems: "center" }}>
        {[0, 1, 2].map(function(i) {
          return <div key={i} style={{ width: 6, height: 6, borderRadius: "50%", background: "#b8f724", animation: "pulse 1.2s infinite", animationDelay: (i * 0.2) + "s", opacity: 0.4 }} />;
        })}
      </div>
    </div>
  );
}

function Message({ msg }) {
  var isUser = msg.role === "user";
  var intent = intentConfig[msg.intent] || intentConfig.GENERAL;
  return (
    <div style={{ display: "flex", alignItems: "flex-start", gap: 10, marginBottom: 16, flexDirection: isUser ? "row-reverse" : "row" }}>
      <div style={{ width: 32, height: 32, borderRadius: 10, flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14, background: isUser ? "#2a2a32" : "#1a2400", border: "1px solid " + (isUser ? "#3a3a42" : "#2d3d00") }}>
        {isUser ? "P" : "💪"}
      </div>
      <div style={{ maxWidth: "78%", display: "flex", flexDirection: "column", gap: 6 }}>
        {!isUser && msg.intent && (
          <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 10, fontWeight: 700, color: intent.color, letterSpacing: "0.08em", textTransform: "uppercase" }}>
            <span>{intent.icon}</span>
            <span>{intent.label}</span>
          </div>
        )}
        <div style={{ background: isUser ? "#1e1e24" : "#1a1a1a", border: "1px solid #2a2a32", borderRadius: isUser ? "12px 4px 12px 12px" : "4px 12px 12px 12px", padding: "12px 16px", fontSize: 14, lineHeight: 1.75, color: "#c8c5be" }}>
          <ReactMarkdown
            components={{
              h1: function(p) { return <h1 style={{fontSize:18,fontWeight:700,color:"#f2f0eb",margin:"8px 0 6px"}}>{p.children}</h1>; },
              h2: function(p) { return <h2 style={{fontSize:16,fontWeight:700,color:"#f2f0eb",margin:"8px 0 6px"}}>{p.children}</h2>; },
              h3: function(p) { return <h3 style={{fontSize:14,fontWeight:700,color:"#f2f0eb",margin:"6px 0 4px"}}>{p.children}</h3>; },
              h4: function(p) { return <h4 style={{fontSize:13,fontWeight:700,color:"#b8f724",margin:"6px 0 4px"}}>{p.children}</h4>; },
              strong: function(p) { return <strong style={{color:"#f2f0eb",fontWeight:700}}>{p.children}</strong>; },
              p: function(p) { return <p style={{margin:"4px 0",lineHeight:1.75}}>{p.children}</p>; },
              ul: function(p) { return <ul style={{paddingLeft:18,margin:"4px 0"}}>{p.children}</ul>; },
              ol: function(p) { return <ol style={{paddingLeft:18,margin:"4px 0"}}>{p.children}</ol>; },
              li: function(p) { return <li style={{margin:"2px 0",lineHeight:1.6}}>{p.children}</li>; },
              hr: function() { return <hr style={{border:"none",borderTop:"1px solid #2a2a32",margin:"10px 0"}} />; },
              table: function(p) { return <div style={{overflowX:"auto",margin:"8px 0"}}><table style={{width:"100%",borderCollapse:"collapse",fontSize:13}}>{p.children}</table></div>; },
              th: function(p) { return <th style={{padding:"6px 10px",background:"#1e1e24",color:"#b8f724",fontWeight:700,textAlign:"left",borderBottom:"1px solid #2a2a32"}}>{p.children}</th>; },
              td: function(p) { return <td style={{padding:"6px 10px",borderBottom:"1px solid #1e1e24",verticalAlign:"top"}}>{p.children}</td>; },
              code: function(p) {
                if (p.inline) {
                  return <code style={{background:"#1e1e24",padding:"1px 6px",borderRadius:4,fontSize:12,color:"#b8f724",fontFamily:"monospace"}}>{p.children}</code>;
                }
                return <pre style={{background:"#111",padding:"10px 12px",borderRadius:8,overflow:"auto",margin:"6px 0"}}><code style={{fontSize:12,color:"#b8f724",fontFamily:"monospace"}}>{p.children}</code></pre>;
              },
            }}
          >
            {msg.content}
          </ReactMarkdown>
          {msg.streaming && <span style={{display:"inline-block",width:2,height:14,background:"#b8f724",marginLeft:2,animation:"pulse 1s infinite",verticalAlign:"middle"}} />}
        </div>
        <div style={{ fontSize: 10, color: "#444", paddingLeft: 4 }}>{msg.time}</div>
      </div>
    </div>
  );
}

function StatCard(props) {
  var color = props.color || "#b8f724";
  return (
    <div style={{ background: "#1a1a1a", border: "1px solid #2a2a32", borderRadius: 12, padding: "14px 16px" }}>
      <div style={{ fontSize: 10, color: "#6b6b7a", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 6, fontWeight: 600 }}>{props.label}</div>
      <div style={{ fontSize: 22, fontWeight: 700, color: color, fontFamily: "monospace", lineHeight: 1 }}>{props.value}</div>
      {props.sub && <div style={{ fontSize: 11, color: "#444", marginTop: 4 }}>{props.sub}</div>}
    </div>
  );
}

function MuscleChip(props) {
  var days = props.days;
  var color = days >= 7 ? "#ff4d6a" : days >= 4 ? "#f0a500" : "#b8f724";
  var bg = days >= 7 ? "#2a0010" : days >= 4 ? "#2a1f00" : "#1a2400";
  var border = days >= 7 ? "#3a0010" : days >= 4 ? "#3a2800" : "#2d3d00";
  return (
    <div style={{ display: "inline-flex", alignItems: "center", gap: 6, background: bg, border: "1px solid " + border, borderRadius: 20, padding: "4px 12px", margin: 3, fontSize: 12, fontWeight: 500, color: color }}>
      <span>{props.muscle}</span>
      <span style={{ opacity: 0.6, fontSize: 10 }}>{days}d</span>
    </div>
  );
}

export default function App() {
  var initMsg = [{
    role: "assistant",
    content: "Hey Prakyath! I am your AI fitness coach. I know your complete training history.\n\nAsk me anything - session coaching, nutrition tracking, progress reports, or weekly planning.",
    time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    intent: null,
  }];

  const [messages, setMessages] = useState(initMsg);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);
  const [tab, setTab] = useState("chat");
  const firstResponseRef = useRef(null);

  useEffect(function() {
    fetch(API + "/stats").then(function(r) { return r.json(); }).then(setStats).catch(function() {});
  }, []);

  // Only scroll to show start of new assistant response
  useEffect(function() {
    var lastMsg = messages[messages.length - 1];
    if (!lastMsg) return;
    // When assistant message first appears (empty content = just started)
    if (lastMsg.role === "assistant" && lastMsg.content === "" && firstResponseRef.current) {
      firstResponseRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [messages.length]);

  async function sendMessage(text) {
    if (!text.trim() || loading) return;
    var time = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    setMessages(function(prev) { return [...prev, { role: "user", content: text, time: time }]; });
    setInput("");
    setLoading(true);

    setMessages(function(prev) { return [...prev, { role: "assistant", content: "", intent: null, time: time, streaming: true }]; });

    try {
      var res = await fetch(API + "/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });

      var reader = res.body.getReader();
      var decoder = new TextDecoder();

      while (true) {
        var result = await reader.read();
        if (result.done) break;

        var lines = decoder.decode(result.value).split("\n");
        for (var i = 0; i < lines.length; i++) {
          var line = lines[i];
          if (!line.startsWith("data: ")) continue;
          try {
            var data = JSON.parse(line.slice(6));

            if (data.type === "intent") {
              var intentVal = data.intent;
              setMessages(function(prev) {
                var updated = prev.slice();
                updated[updated.length - 1] = Object.assign({}, updated[updated.length - 1], { intent: intentVal });
                return updated;
              });
            }

            if (data.type === "token") {
              var chars = data.token.split("");
              for (var c = 0; c < chars.length; c++) {
                var ch = chars[c];
                await new Promise(function(resolve) { setTimeout(resolve, 12); });
                setMessages(function(prev) {
                  var updated = prev.slice();
                  var last = updated[updated.length - 1];
                  updated[updated.length - 1] = Object.assign({}, last, { content: last.content + ch });
                  return updated;
                });
              }
            }

            if (data.type === "done") {
              setMessages(function(prev) {
                var updated = prev.slice();
                updated[updated.length - 1] = Object.assign({}, updated[updated.length - 1], { streaming: false });
                return updated;
              });
            }
          } catch(e) {}
        }
      }
    } catch(e) {
      setMessages(function(prev) {
        var updated = prev.slice();
        updated[updated.length - 1] = { role: "assistant", content: "Connection error. Make sure FastAPI is running on port 8000.", time: time, streaming: false };
        return updated;
      });
    }
    setLoading(false);
  }

  return (
    <div style={{ height: "100vh", background: "#0e0e10", color: "#f2f0eb", fontFamily: "'Inter','Segoe UI',system-ui,sans-serif", display: "flex", flexDirection: "column", maxWidth: 480, margin: "0 auto" }}>
      <style dangerouslySetInnerHTML={{__html: "@keyframes pulse{0%,100%{opacity:.3;transform:scale(1)}50%{opacity:1;transform:scale(1.3)}}*{box-sizing:border-box;margin:0;padding:0}::-webkit-scrollbar{width:3px}::-webkit-scrollbar-thumb{background:#2a2a32;border-radius:2px}"}} />

      <div style={{ padding: "16px 20px 12px", background: "rgba(14,14,16,0.95)", borderBottom: "1px solid #1a1a1a", flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 36, height: 36, background: "#b8f724", borderRadius: 10, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18 }}>💪</div>
          <div>
            <div style={{ fontSize: 16, fontWeight: 700 }}>FitMind</div>
            <div style={{ fontSize: 11, color: "#4ade80", display: "flex", alignItems: "center", gap: 4 }}>
              <div style={{ width: 5, height: 5, borderRadius: "50%", background: "#4ade80", animation: "pulse 2s infinite" }} />
              AI Coach Online
            </div>
          </div>
        </div>
        <div style={{ display: "flex", gap: 2, background: "#1a1a1a", borderRadius: 10, padding: 3 }}>
          {["chat", "stats"].map(function(t) {
            return (
              <button key={t} onClick={function() { setTab(t); }} style={{ padding: "6px 14px", borderRadius: 8, border: "none", cursor: "pointer", fontSize: 12, fontWeight: 600, background: tab === t ? "#b8f724" : "transparent", color: tab === t ? "#000" : "#666" }}>
                {t === "chat" ? "💬 Coach" : "📊 Stats"}
              </button>
            );
          })}
        </div>
      </div>

      {tab === "chat" && (
        <div style={{ display: "flex", flexDirection: "column", flex: 1, overflow: "hidden" }}>
          <div style={{ flex: 1, overflowY: "auto", padding: "20px 16px 0" }}>
            {messages.length <= 1 && (
              <div style={{ marginBottom: 20 }}>
                <div style={{ fontSize: 10, fontWeight: 700, color: "#444", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 10 }}>Quick actions</div>
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {suggestions.map(function(s, i) {
                    return (
                      <button key={i} onClick={function() { sendMessage(s.text); }} style={{ background: "#1a1a1a", border: "1px solid #2a2a32", borderRadius: 12, padding: "11px 14px", cursor: "pointer", color: "#b8b5b0", fontSize: 13, textAlign: "left", display: "flex", alignItems: "center", gap: 10 }}>
                        <span style={{ fontSize: 16 }}>{s.icon}</span>
                        <span>{s.text}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {messages.map(function(msg, i) {
              var isLastAssistant = i === messages.length - 1 && msg.role === "assistant";
              return (
                <div key={i} ref={isLastAssistant ? firstResponseRef : null}>
                  <Message msg={msg} />
                </div>
              );
            })}

            {loading && messages[messages.length - 1] && messages[messages.length - 1].content === "" && <TypingIndicator />}
            <div style={{ height: 16 }} />
          </div>

          <div style={{ padding: "12px 16px 20px", background: "rgba(14,14,16,0.98)", borderTop: "1px solid #1a1a1a", flexShrink: 0 }}>
            <div style={{ display: "flex", alignItems: "flex-end", gap: 8, background: "#1a1a1a", border: "1px solid #2a2a32", borderRadius: 20, padding: "6px 6px 6px 16px" }}>
              <textarea
                value={input}
                onChange={function(e) {
                  setInput(e.target.value);
                  e.target.style.height = "auto";
                  e.target.style.height = Math.min(e.target.scrollHeight, 120) + "px";
                }}
                onKeyDown={function(e) {
                  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(input); }
                }}
                placeholder="Message your coach..."
                rows={1}
                style={{ flex: 1, background: "none", border: "none", outline: "none", color: "#f2f0eb", fontSize: 14, lineHeight: 1.5, resize: "none", padding: "8px 0", minHeight: 38, maxHeight: 120, fontFamily: "inherit" }}
              />
              <button
                onClick={function() { sendMessage(input); }}
                disabled={loading || !input.trim()}
                style={{ width: 36, height: 36, borderRadius: "50%", border: "none", background: input.trim() && !loading ? "#b8f724" : "#2a2a32", color: input.trim() && !loading ? "#000" : "#444", cursor: input.trim() && !loading ? "pointer" : "not-allowed", fontSize: 16, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}
              >↑</button>
            </div>
            <div style={{ fontSize: 10, color: "#333", textAlign: "center", marginTop: 8 }}>LangGraph · Mistral AI · Qdrant · Hybrid RAG</div>
          </div>
        </div>
      )}

      {tab === "stats" && (
        <div style={{ flex: 1, overflowY: "auto", padding: 16 }}>
          {!stats ? (
            <div style={{ color: "#444", fontSize: 13, textAlign: "center", marginTop: 40 }}>Loading stats... Make sure FastAPI is running on port 8000.</div>
          ) : stats.error ? (
            <div style={{ color: "#ff4d6a", fontSize: 13, padding: 16, background: "#2a0010", borderRadius: 12 }}>Error loading stats.</div>
          ) : (
            <div>
              <div style={{ fontSize: 10, fontWeight: 700, color: "#444", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 12 }}>Daily targets</div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 20 }}>
                <StatCard label="Protein" value={stats.protein_target + "g"} sub="daily target" color="#b8f724" />
                <StatCard label="Calories" value={stats.calorie_target} sub="daily target" color="#f0a500" />
                <StatCard label="Goal" value={stats.goal ? stats.goal.toUpperCase() : ""} sub="current focus" color="#a78bfa" />
                <StatCard label="Undertrained" value={stats.undertrained ? stats.undertrained.length : 0} sub="muscles" color={stats.undertrained && stats.undertrained.length > 0 ? "#ff4d6a" : "#4ade80"} />
              </div>

              {stats.undertrained && stats.undertrained.length > 0 && (
                <div>
                  <div style={{ fontSize: 10, fontWeight: 700, color: "#444", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 10 }}>Needs attention</div>
                  <div style={{ marginBottom: 20 }}>
                    {stats.undertrained.map(function(m) {
                      return <MuscleChip key={m} muscle={m} days={stats.freshness && stats.freshness[m] ? stats.freshness[m] : 7} />;
                    })}
                  </div>
                </div>
              )}

              {stats.freshness && Object.keys(stats.freshness).length > 0 && (
                <div>
                  <div style={{ fontSize: 10, fontWeight: 700, color: "#444", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 10 }}>Muscle recovery</div>
                  <div style={{ background: "#1a1a1a", border: "1px solid #2a2a32", borderRadius: 12, overflow: "hidden" }}>
                    {Object.entries(stats.freshness).sort(function(a, b) { return a[1] - b[1]; }).map(function(entry, i, arr) {
                      var muscle = entry[0];
                      var days = entry[1];
                      var pct = Math.min((days / 14) * 100, 100);
                      var color = days >= 7 ? "#ff4d6a" : days >= 4 ? "#f0a500" : "#b8f724";
                      return (
                        <div key={muscle} style={{ padding: "12px 14px", borderBottom: i < arr.length - 1 ? "1px solid #1e1e24" : "none" }}>
                          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                            <span style={{ fontSize: 12, fontWeight: 500 }}>{muscle}</span>
                            <span style={{ fontSize: 11, color: color, fontFamily: "monospace" }}>{days}d ago</span>
                          </div>
                          <div style={{ height: 4, background: "#111", borderRadius: 2, overflow: "hidden" }}>
                            <div style={{ height: "100%", width: pct + "%", background: color, borderRadius: 2 }} />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              <button onClick={function() { setTab("chat"); }} style={{ width: "100%", padding: 14, background: "#b8f724", color: "#000", border: "none", borderRadius: 12, fontSize: 14, fontWeight: 700, cursor: "pointer", marginTop: 20 }}>
                💬 Ask your coach
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
