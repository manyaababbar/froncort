import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import { v4 as uuidv4 } from "uuid";
import "./App.css";

const API_URL = import.meta.env.VITE_REACT_APP_FASTAPI_URL || "http://localhost:8000";
console.log("🔧 API URL:", API_URL);

const USER_ID_KEY = "chat_user_id";
const SESSIONS_KEY = "chat_sessions";
const CONVS_KEY = "chat_conversations";

export default function App() {
  const [userId, setUserId] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [conversations, setConversations] = useState({});
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [ensuring, setEnsuring] = useState(false);
  const [apiStatus, setApiStatus] = useState("checking");
  const messagesEndRef = useRef(null);
  const hasInitialized = useRef(false);

  const THINKING_PREFIX = "Thinking";

  function loadLocalState() {
    const uid = localStorage.getItem(USER_ID_KEY) || null;
    const savedSessions = JSON.parse(localStorage.getItem(SESSIONS_KEY) || "[]");
    const savedConvs = JSON.parse(localStorage.getItem(CONVS_KEY) || "{}");
    return { uid, savedSessions, savedConvs };
  }

  function saveSessionsToLocal(sessions) {
    localStorage.setItem(SESSIONS_KEY, JSON.stringify(sessions));
  }

  function saveConversationsToLocal(convs) {
    localStorage.setItem(CONVS_KEY, JSON.stringify(convs));
  }

  async function checkApiConnection() {
    try {
      console.log("🔍 Testing API:", `${API_URL}/debug/db-test`);
      const response = await axios.get(`${API_URL}/debug/db-test`, { timeout: 5000 });
      console.log("✅ API OK:", response.data);
      setApiStatus("connected");
      return true;
    } catch (error) {
      console.error("❌ API failed:", error.message);
      setApiStatus("disconnected");
      return false;
    }
  }

  useEffect(() => {
    if (hasInitialized.current) return;
    hasInitialized.current = true;

    (async () => {
      const apiReachable = await checkApiConnection();

      let uid = localStorage.getItem(USER_ID_KEY);
      if (!uid) {
        uid = uuidv4();
        localStorage.setItem(USER_ID_KEY, uid);
      }
      setUserId(uid);

      const { savedSessions, savedConvs } = loadLocalState();
      setConversations(savedConvs || {});

      if (savedSessions.length > 0) {
        setSessions(savedSessions);
        const first = savedSessions[0];

        if (apiReachable) {
          await ensureAndLoad(uid, first, { selectAfterLoad: true, showCachedFirst: true });
        } else {
          setActiveSession(first);
        }
      } else {
        const sid = `session_${Date.now()}`;
        setSessions([sid]);
        setConversations({ [sid]: [] });
        saveSessionsToLocal([sid]);
        saveConversationsToLocal({ [sid]: [] });

        if (apiReachable) {
          await ensureAndLoad(uid, sid, { selectAfterLoad: true, showCachedFirst: false });
        } else {
          setActiveSession(sid);
        }
      }
    })();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [conversations, activeSession, loading]);

  async function ensureSessionOnServer(uid, sessionId) {
    setEnsuring(true);
    try {
      console.log("📡 Ensuring session:", { uid, sessionId, url: `${API_URL}/sessions/ensure` });

      const response = await axios.post(
        `${API_URL}/sessions/ensure`,
        { user_id: uid, session_id: sessionId },
        { timeout: 10000 }
      );

      console.log("✅ Session ensured:", response.data);
      return true;
    } catch (err) {
      console.error("❌ ensureSession error:", err.message);
      return false;
    } finally {
      setEnsuring(false);
    }
  }

  async function fetchHistoryFromServer(uid, sessionId) {
    try {
      const url = `${API_URL}/history/${encodeURIComponent(uid)}/${encodeURIComponent(sessionId)}`;
      console.log("📡 Fetching history:", url);

      const res = await axios.get(url, { timeout: 10000 });
      return Array.isArray(res.data.messages) ? res.data.messages : [];
    } catch (err) {
      console.error("❌ fetchHistory error:", err.message);
      return null;
    }
  }

  async function ensureAndLoad(uid, sessionId, opts = { selectAfterLoad: true, showCachedFirst: true }) {
    if (opts.showCachedFirst) setActiveSession(sessionId);

    await ensureSessionOnServer(uid, sessionId);
    const serverMsgs = await fetchHistoryFromServer(uid, sessionId);

    setConversations((prev) => {
      const cached = prev[sessionId] || [];
      const finalMsgs = Array.isArray(serverMsgs) && serverMsgs.length > 0 ? serverMsgs : cached;

      const next = { ...prev, [sessionId]: finalMsgs };
      saveConversationsToLocal(next);
      return next;
    });

    if (opts.selectAfterLoad) setActiveSession(sessionId);
  }

  async function createAndSelectSession(uid, sessionId) {
    setSessions((prev) => {
      if (prev.includes(sessionId)) return prev;
      const next = [sessionId, ...prev];
      saveSessionsToLocal(next);
      return next;
    });

    setConversations((prev) => {
      const next = { ...prev, [sessionId]: [] };
      saveConversationsToLocal(next);
      return next;
    });

    if (apiStatus === "connected") {
      await ensureAndLoad(uid, sessionId, { selectAfterLoad: true, showCachedFirst: true });
    } else {
      setActiveSession(sessionId);
    }
  }

  async function handleSelectSession(sessionId) {
    await ensureAndLoad(userId, sessionId, { selectAfterLoad: true, showCachedFirst: true });
  }

  async function handleNewChat() {
    const newId = `session_${Date.now()}`;
    await createAndSelectSession(userId, newId);
  }

  function handleDeleteSession(id) {
    setSessions((prev) => {
      const next = prev.filter((s) => s !== id);
      saveSessionsToLocal(next);
      return next;
    });

    setConversations((prev) => {
      const next = { ...prev };
      delete next[id];
      saveConversationsToLocal(next);
      return next;
    });

    if (activeSession === id) {
      const remaining = sessions.filter((s) => s !== id);
      setActiveSession(remaining[0] || null);
    }
  }

  async function handleSend(e) {
    e?.preventDefault();
    if (!input.trim() || !activeSession) return;

    if (apiStatus === "disconnected") {
      alert("⚠ API is offline. Start FastAPI server.");
      return;
    }

    const userMsg = { sender: "user", text: input };

    setConversations((prev) => {
      const next = { ...prev };
      next[activeSession] = [...(next[activeSession] || []), userMsg];
      saveConversationsToLocal(next);
      return next;
    });

    const thinkingId = `${THINKING_PREFIX}${Date.now()}`;
    setConversations((prev) => {
      const next = { ...prev };
      next[activeSession] = [
        ...(next[activeSession] || []),
        { sender: "bot", text: "", temp: true, tempId: thinkingId },
      ];
      saveConversationsToLocal(next);
      return next;
    });

    const payload = {
      user_query: input,
      user_id: userId,
      session_id: activeSession,
    };

    setInput("");
    setLoading(true);

    try {
      console.log("📡 Chat request →", `${API_URL}/chat`, payload);

      await ensureSessionOnServer(userId, activeSession);

      const res = await axios.post(`${API_URL}/chat`, payload, {
        timeout: 120000,
        headers: { "Content-Type": "application/json" },
      });

      const botText = res.data?.response || res.data?.result || res.data?.answer || "No response";
      const aiMsg = { sender: "bot", text: botText };

      setConversations((prev) => {
        const prevMessages = prev[activeSession] || [];

        const newMessages = prevMessages.map((m) =>
          m.temp && m.tempId === thinkingId ? aiMsg : m
        );

        setTimeout(() => saveConversationsToLocal({ ...prev, [activeSession]: newMessages }), 0);

        return { ...prev, [activeSession]: newMessages };
      });
    } catch (err) {
      let errorText = "Sorry — I couldn't process that.";

      if (err.code === "ECONNREFUSED" || err.code === "ERR_NETWORK") {
        errorText += " Server offline.";
        setApiStatus("disconnected");
      }

      const errMsg = { sender: "bot", text: errorText };

      setConversations((prev) => {
        const newMessages = prev[activeSession].map((m) =>
          m.temp && m.tempId === thinkingId ? errMsg : m
        );
        return { ...prev, [activeSession]: newMessages };
      });
    } finally {
      setLoading(false);
    }
  }

  const activeMessages = conversations[activeSession] || [];

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h3>Sessions</h3>
          <button className="new-btn" onClick={handleNewChat} disabled={ensuring}>
            + New
          </button>
        </div>

        <div
          style={{
            padding: "8px 16px",
            background: apiStatus === "connected" ? "#d4edda" : "#f8d7da",
            color: apiStatus === "connected" ? "#155724" : "#721c24",
            fontSize: "12px",
            borderRadius: "4px",
            margin: "8px",
          }}
        >
          API: {apiStatus === "connected" ? "✅ Connected" : "❌ Disconnected"}
        </div>

        <div className="session-list">
          {sessions.map((sid) => (
            <div
              key={sid}
              className={`session-item ${sid === activeSession ? "active" : ""}`}
              onClick={() => handleSelectSession(sid)}
            >
              <div className="session-title">{sid}</div>
              <div className="session-actions">
                <button
                  className="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteSession(sid);
                  }}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="sidebar-footer">
          <div className="user-id">User: {userId?.slice(0, 8)}...</div>
        </div>
      </aside>

      <main className="chat-panel">
        <div className="chat-header">
          <h2>{activeSession ? `Session: ${activeSession}` : "No session selected"}</h2>
          {loading && <div className="loading-indicator">Thinking…</div>}
        </div>

        <div className="messages">
          {activeMessages.length === 0 && !loading && (
            <div className="empty-chat">Start the conversation — say hi 👋</div>
          )}

          {activeMessages.map((m, i) => (
            <div key={i} className={`message-row ${m.sender}`}>
              <div
                className={
                  m.temp
                    ? "bubble thinking-bubble"
                    : `bubble ${m.sender === "user" ? "user-bubble" : "bot-bubble"}`
                }
              >
                {m.temp ? (
                  <span className="thinking-dots" aria-hidden>
                    <span className="dot d1" />
                    <span className="dot d2" />
                    <span className="dot d3" />
                  </span>
                ) : (
                  m.text
                )}
              </div>
            </div>
          ))}

          <div ref={messagesEndRef} />
        </div>

        <form className="composer" onSubmit={handleSend}>
          <input
            placeholder="Type a message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={!activeSession || loading}
          />
          <button type="submit" disabled={!input.trim() || loading}>
            Send
          </button>
        </form>
      </main>
    </div>
  );
}
