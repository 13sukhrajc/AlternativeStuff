import { useState, useEffect } from "react";

const fontLink = document.createElement("link");
fontLink.href = "https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800;900&display=swap";
fontLink.rel = "stylesheet";
document.head.appendChild(fontLink);

const API_URL = "http://localhost:8000";

const REGIONS = {
  CA: { label: "🇨🇦 Canada", currency: "CAD", flag: "🇨🇦" },
  US: { label: "🇺🇸 USA",    currency: "USD", flag: "🇺🇸" },
};

const TIER_CONFIG = [
  { key: "count_budget",   label: "Budget",     color: "#16a34a", desc: "Cheaper alternatives" },
  { key: "count_mid",      label: "Competitor", color: "#2563eb", desc: "Similar price & features" },
  { key: "count_premium",  label: "Premium",    color: "#b45309", desc: "Higher-end options" },
  { key: "count_next_gen", label: "Next-Gen",   color: "#7c3aed", desc: "Latest releases" },
];

const TIER_STYLES = {
  budget:     { color: "#16a34a", lightBg: "#f0fdf4", lightBorder: "#bbf7d0", darkBg: "#052e16", darkBorder: "#166534", label: "Budget" },
  mid:        { color: "#2563eb", lightBg: "#eff6ff", lightBorder: "#bfdbfe", darkBg: "#0c1a3a", darkBorder: "#1e40af", label: "Competitor" },
  premium:    { color: "#b45309", lightBg: "#fffbeb", lightBorder: "#fde68a", darkBg: "#2d1a00", darkBorder: "#92400e", label: "Premium" },
  "next-gen": { color: "#7c3aed", lightBg: "#faf5ff", lightBorder: "#e9d5ff", darkBg: "#1e0a3a", darkBorder: "#5b21b6", label: "Next-Gen" },
  original:   { color: "#64748b", lightBg: "#f8fafc", lightBorder: "#e2e8f0", darkBg: "#1e293b", darkBorder: "#334155", label: "Original" },
};

const TIER_ORDER = ["original", "budget", "mid", "premium", "next-gen"];

const THEME = {
  light: {
    pageBg: "#f4f6f9", navBg: "#ffffff", navBorder: "#e8ecf0",
    cardBg: "#ffffff", cardBorder: "#e8ecf0",
    boxBg: "#ffffff", boxBorder: "#e8ecf0",
    inputBg: "#f8fafc", inputBorder: "#e2e8f0", inputColor: "#0f172a",
    toggleTrack: "#e2e8f0", toggleActive: "#0f172a",
    btnBg: "#0f172a", btnColor: "#ffffff", btnDisabled: "#e2e8f0",
    text: "#1e293b", textMuted: "#94a3b8", textStrong: "#0f172a",
    stepperBg: "#f1f5f9", stepperBorder: "#e2e8f0", stepperColor: "#64748b",
    regionBg: "#f1f5f9", regionBorder: "#e2e8f0", regionActive: "#ffffff",
    regionShadow: "0 1px 3px rgba(0,0,0,0.08)",
    shadow: "0 2px 12px rgba(0,0,0,0.05)",
    cardShadow: "0 1px 4px rgba(0,0,0,0.06)",
    cardHoverShadow: "0 8px 24px rgba(0,0,0,0.10)",
    imageBg: "#f8fafc", imageBorder: "#f1f5f9", divider: "#f1f5f9",
    errorBg: "#fef2f2", errorBorder: "#fecaca", errorColor: "#dc2626",
    spinnerTrack: "#e2e8f0", spinnerHead: "#0f172a", modeIcon: "🌙",
  },
  dark: {
    pageBg: "#0a0f1a", navBg: "#0f172a", navBorder: "#1e293b",
    cardBg: "#0f172a", cardBorder: "#1e293b",
    boxBg: "#0f172a", boxBorder: "#1e293b",
    inputBg: "#1e293b", inputBorder: "#334155", inputColor: "#f1f5f9",
    toggleTrack: "#334155", toggleActive: "#60a5fa",
    btnBg: "#3b82f6", btnColor: "#ffffff", btnDisabled: "#1e293b",
    text: "#cbd5e1", textMuted: "#475569", textStrong: "#f1f5f9",
    stepperBg: "#1e293b", stepperBorder: "#334155", stepperColor: "#94a3b8",
    regionBg: "#1e293b", regionBorder: "#334155", regionActive: "#334155",
    regionShadow: "0 1px 3px rgba(0,0,0,0.3)",
    shadow: "0 2px 16px rgba(0,0,0,0.3)",
    cardShadow: "0 1px 4px rgba(0,0,0,0.3)",
    cardHoverShadow: "0 8px 28px rgba(0,0,0,0.5)",
    imageBg: "#1e293b", imageBorder: "#334155", divider: "#1e293b",
    errorBg: "#2d0a0a", errorBorder: "#7f1d1d", errorColor: "#fca5a5",
    spinnerTrack: "#1e293b", spinnerHead: "#60a5fa", modeIcon: "☀️",
  },
};

const FONT = "'Nunito', sans-serif";

// ---------------------------------------------------------------------------
// Components
// ---------------------------------------------------------------------------

function TierBadge({ tier, t }) {
  const s = TIER_STYLES[tier] || TIER_STYLES.original;
  const isDark = t === THEME.dark;
  return (
    <span style={{
      background: isDark ? s.darkBg : s.lightBg,
      color: s.color,
      border: `1px solid ${isDark ? s.darkBorder : s.lightBorder}`,
      borderRadius: 20, padding: "3px 10px",
      fontSize: 11, fontWeight: 800,
      letterSpacing: "0.06em", textTransform: "uppercase",
      fontFamily: FONT, whiteSpace: "nowrap", flexShrink: 0,
    }}>
      {s.label}
    </span>
  );
}

function CountStepper({ value, onChange, t }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6, flexShrink: 0 }}>
      <button onClick={() => onChange(Math.max(0, value - 1))} style={{
        width: 26, height: 26, borderRadius: 6,
        background: t.stepperBg, border: `1px solid ${t.stepperBorder}`,
        color: t.stepperColor, cursor: "pointer", fontSize: 15, fontWeight: 700,
        display: "flex", alignItems: "center", justifyContent: "center",
        transition: "background 0.15s", fontFamily: FONT,
      }}>−</button>
      <span style={{
        width: 22, textAlign: "center",
        color: t.textStrong, fontWeight: 800, fontSize: 14, fontFamily: FONT,
      }}>{value}</span>
      <button onClick={() => onChange(Math.min(10, value + 1))} style={{
        width: 26, height: 26, borderRadius: 6,
        background: t.stepperBg, border: `1px solid ${t.stepperBorder}`,
        color: t.stepperColor, cursor: "pointer", fontSize: 15, fontWeight: 700,
        display: "flex", alignItems: "center", justifyContent: "center",
        transition: "background 0.15s", fontFamily: FONT,
      }}>+</button>
    </div>
  );
}

function ProductCard({ product, t, index }) {
  const imageUrl = typeof product.image === "object" ? product.image?.link : product.image;
  const merchant = product.merchants?.[0];
  const s = TIER_STYLES[product.tier] || TIER_STYLES.original;
  const isDark = t === THEME.dark;

  // Staggered fade-in — each card delays 40ms per index
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const timer = setTimeout(() => setVisible(true), index * 40);
    return () => clearTimeout(timer);
  }, [index]);

  return (
    <div
      style={{
        background: t.cardBg,
        border: `1px solid ${t.cardBorder}`,
        borderRadius: 16,
        overflow: "hidden",
        boxShadow: t.cardShadow,
        display: "flex",
        flexDirection: "column",
        height: "100%",
        boxSizing: "border-box",
        // Staggered fade + slide up on entry
        opacity: visible ? 1 : 0,
        transform: visible ? "translateY(0)" : "translateY(18px)",
        transition: "opacity 0.4s ease, transform 0.4s ease, box-shadow 0.2s, border-color 0.2s",
      }}
      onMouseEnter={e => {
        e.currentTarget.style.boxShadow = t.cardHoverShadow;
        e.currentTarget.style.transform = "translateY(-3px)";
        e.currentTarget.style.borderColor = isDark ? s.darkBorder : s.lightBorder;
      }}
      onMouseLeave={e => {
        e.currentTarget.style.boxShadow = t.cardShadow;
        e.currentTarget.style.transform = "translateY(0)";
        e.currentTarget.style.borderColor = t.cardBorder;
      }}
    >
      {/* Tier colour stripe */}
      <div style={{ height: 4, background: s.color, opacity: 0.8, flexShrink: 0 }} />

      {/* Image */}
      <div style={{
        height: 150, flexShrink: 0, background: t.imageBg,
        display: "flex", alignItems: "center", justifyContent: "center",
        borderBottom: `1px solid ${t.imageBorder}`,
        padding: 8, overflow: "hidden",
      }}>
        {imageUrl
          ? <img src={imageUrl} alt="" style={{ maxHeight: "100%", maxWidth: "100%", objectFit: "contain", display: "block" }} />
          : <div style={{ color: t.textMuted, fontSize: 28 }}>📦</div>
        }
      </div>

      {/* Content */}
      <div style={{
        padding: "12px 14px 14px", flex: 1,
        display: "flex", flexDirection: "column",
        minHeight: 0, overflow: "hidden",
      }}>
        <div style={{ marginBottom: 8, flexShrink: 0 }}>
          <TierBadge tier={product.tier} t={t} />
        </div>

        <p style={{
          color: t.text, fontSize: 13, fontWeight: 600,
          lineHeight: 1.45, margin: 0, fontFamily: FONT,
          display: "-webkit-box", WebkitLineClamp: 3,
          WebkitBoxOrient: "vertical", overflow: "hidden",
          wordBreak: "break-word", flex: 1, marginBottom: 12,
        }}>
          {product.title}
        </p>

        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexShrink: 0, gap: 8 }}>
          <div style={{ minWidth: 0 }}>
            <span style={{ color: t.textStrong, fontWeight: 800, fontSize: 16, fontFamily: FONT, whiteSpace: "nowrap" }}>
              {merchant?.price != null ? `$${merchant.price.toFixed(2)}` : "—"}
            </span>
            {merchant?.merchant && (
              <div style={{ color: t.textMuted, fontSize: 11, fontFamily: FONT, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {merchant.merchant}
              </div>
            )}
          </div>

          {merchant?.affiliate_link && (
            <a href={merchant.affiliate_link} target="_blank" rel="noopener noreferrer"
              style={{
                background: t.btnBg, color: t.btnColor,
                padding: "6px 12px", borderRadius: 8,
                fontSize: 12, fontWeight: 700, textDecoration: "none",
                transition: "opacity 0.15s", letterSpacing: "0.03em",
                fontFamily: FONT, whiteSpace: "nowrap", flexShrink: 0,
              }}
              onMouseEnter={e => e.currentTarget.style.opacity = "0.82"}
              onMouseLeave={e => e.currentTarget.style.opacity = "1"}
            >
              View →
            </a>
          )}
        </div>

        {product.merchants?.length > 1 && (
          <div style={{ marginTop: 10, paddingTop: 10, borderTop: `1px solid ${t.divider}`, flexShrink: 0 }}>
            {product.merchants.slice(1).map(m => (
              <div key={m.merchant} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4, gap: 8 }}>
                <span style={{ color: t.textMuted, fontSize: 12, fontFamily: FONT, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {m.merchant}
                </span>
                <a href={m.affiliate_link} target="_blank" rel="noopener noreferrer"
                  style={{ color: "#3b82f6", fontSize: 12, fontWeight: 700, fontFamily: FONT, whiteSpace: "nowrap", flexShrink: 0 }}>
                  {m.price != null ? `$${m.price.toFixed(2)}` : "View"}
                </a>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main App
// ---------------------------------------------------------------------------

export default function App() {
  const [darkMode, setDarkMode]             = useState(false);
  const [query, setQuery]                   = useState("");
  const [region, setRegion]                 = useState("CA");
  const [budgetEnabled, setBudgetEnabled]   = useState(false);
  const [budgetMin, setBudgetMin]           = useState("");
  const [budgetMax, setBudgetMax]           = useState("");
  const [tierCounts, setTierCounts]         = useState({ count_budget: 1, count_mid: 2, count_premium: 1, count_next_gen: 1 });
  const [results, setResults]               = useState(null);
  const [loading, setLoading]               = useState(false);
  const [error, setError]                   = useState(null);
  const [resultsVisible, setResultsVisible] = useState(false);
  const [status, setStatus]                 = useState("");

  const t        = darkMode ? THEME.dark : THEME.light;
  const total    = Object.values(tierCounts).reduce((a, b) => a + b, 0);
  const currency = REGIONS[region].currency;
  const hasResults = !!(results && !loading);

  const handleSearch = async () => {
    if (!query.trim()) return;
    if (total === 0) { setError("Select at least 1 substitute"); return; }
    if (total > 15)  { setError("Maximum 15 total substitutes"); return; }

    setLoading(true);
    setError(null);
    setResults(null);
    setResultsVisible(false);
    setStatus("Asking AI for alternatives...");

    try {
      const res = await fetch(`${API_URL}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: query.trim(), region, ...tierCounts,
          budget_min: budgetEnabled && budgetMin !== "" ? parseFloat(budgetMin) : null,
          budget_max: budgetEnabled && budgetMax !== "" ? parseFloat(budgetMax) : null,
        }),
      });

      setStatus("Looking up prices on Amazon...");

      if (!res.ok) { const e = await res.json(); throw new Error(e.detail || "Search failed"); }
      const data = await res.json();
      setResults(data);
      setStatus("");
      // Short delay so search box finishes sliding up before cards appear
      setTimeout(() => setResultsVisible(true), 120);
    } catch (e) {
      setError(e.message);
      setStatus("");
    } finally {
      setLoading(false);
    }
  };

  const sortedProducts = results?.products
    ? [...results.products].sort((a, b) => TIER_ORDER.indexOf(a.tier) - TIER_ORDER.indexOf(b.tier))
    : [];

  return (
    <div style={{
      minHeight: "100vh",
      background: t.pageBg,
      color: t.text,
      fontFamily: FONT,
      transition: "background 0.3s, color 0.3s",
    }}>
      <style>{`
        @keyframes spin    { to { transform: rotate(360deg); } }
        @keyframes fadeDown {
          from { opacity: 0; transform: translateY(-10px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}</style>

      {/* ── Navbar ── */}
      <div style={{
        background: t.navBg, borderBottom: `1px solid ${t.navBorder}`,
        padding: "0 24px", display: "flex", alignItems: "center",
        justifyContent: "space-between", height: 60,
        boxShadow: "0 1px 3px rgba(0,0,0,0.04)",
        position: "sticky", top: 0, zIndex: 100,
        transition: "background 0.3s, border-color 0.3s",
      }}>
        {/* Left — dark mode toggle */}
        <button
          onClick={() => setDarkMode(d => !d)}
          title={darkMode ? "Light mode" : "Dark mode"}
          style={{
            width: 38, height: 38, borderRadius: 10,
            background: t.stepperBg, border: `1px solid ${t.stepperBorder}`,
            cursor: "pointer", fontSize: 17,
            display: "flex", alignItems: "center", justifyContent: "center",
            transition: "background 0.2s", flexShrink: 0,
          }}
          onMouseEnter={e => e.currentTarget.style.background = t.regionBorder}
          onMouseLeave={e => e.currentTarget.style.background = t.stepperBg}
        >
          {t.modeIcon}
        </button>

        {/* Center — title */}
        <div style={{
          position: "absolute", left: "50%", transform: "translateX(-50%)",
          display: "flex", alignItems: "baseline", gap: 8, pointerEvents: "none",
        }}>
          <span style={{ fontSize: 22, fontWeight: 900, color: t.textStrong, letterSpacing: "-0.02em", fontFamily: FONT }}>
            BuyBuzz
          </span>
          <span style={{ fontSize: 12, color: t.textMuted, fontFamily: FONT }}>product alternatives</span>
        </div>

        {/* Right — region toggle */}
        <div style={{
          display: "flex", background: t.regionBg, borderRadius: 10,
          padding: 3, gap: 2, border: `1px solid ${t.regionBorder}`, flexShrink: 0,
        }}>
          {Object.entries(REGIONS).map(([key, r]) => (
            <button key={key} onClick={() => setRegion(key)} style={{
              padding: "6px 14px", borderRadius: 8, border: "none",
              background: region === key ? t.regionActive : "transparent",
              color: region === key ? t.textStrong : t.textMuted,
              fontWeight: region === key ? 800 : 500,
              fontSize: 13, cursor: "pointer",
              boxShadow: region === key ? t.regionShadow : "none",
              transition: "all 0.15s", fontFamily: FONT,
            }}>
              {r.label}
            </button>
          ))}
        </div>
      </div>

      {/* ── Main content ── */}
      {/*
        Before search: flexbox centers the search box vertically on screen.
        After results: justifyContent flips to flex-start, box slides to top.
      */}
      <div style={{
        minHeight: "calc(100vh - 60px)",
        display: "flex",
        flexDirection: "column",
        justifyContent: hasResults || loading ? "flex-start" : "center",
        transition: "justify-content 0.5s ease",
      }}>
        <div style={{
          maxWidth: 1140, width: "100%", margin: "0 auto",
          padding: hasResults || loading ? "28px 24px 40px" : "0 24px 80px",
          transition: "padding 0.5s cubic-bezier(0.4, 0, 0.2, 1)",
          boxSizing: "border-box",
        }}>

          {/* ── Search box ── */}
          <div style={{
            background: t.boxBg, borderRadius: 20,
            border: `1px solid ${t.boxBorder}`,
            boxShadow: t.shadow, padding: "32px 36px",
            maxWidth: 860, margin: "0 auto 28px",
            transition: "background 0.3s, border-color 0.3s",
          }}>
            <p style={{ margin: "0 0 14px", fontSize: 13, color: t.textMuted, fontFamily: FONT }}>
              Paste an Amazon URL or type a product name
            </p>

            {/* Input row */}
            <div style={{ display: "flex", gap: 10 }}>
              <input
                value={query}
                onChange={e => setQuery(e.target.value)}
                onKeyDown={e => e.key === "Enter" && handleSearch()}
                placeholder={`Search on Amazon ${REGIONS[region].flag}...`}
                style={{
                  flex: 1, padding: "13px 18px",
                  background: t.inputBg, border: `1px solid ${t.inputBorder}`,
                  borderRadius: 10, color: t.inputColor, fontSize: 14,
                  outline: "none", transition: "border-color 0.2s", fontFamily: FONT,
                }}
                onFocus={e => e.target.style.borderColor = "#60a5fa"}
                onBlur={e => e.target.style.borderColor = t.inputBorder}
              />
              <button
                onClick={handleSearch}
                disabled={loading || !query.trim() || total === 0}
                style={{
                  padding: "13px 28px",
                  background: loading || !query.trim() ? t.btnDisabled : t.btnBg,
                  border: "none", borderRadius: 10,
                  color: loading || !query.trim() ? t.textMuted : t.btnColor,
                  fontWeight: 800, fontSize: 14,
                  cursor: loading || !query.trim() ? "not-allowed" : "pointer",
                  opacity: total === 0 ? 0.4 : 1,
                  transition: "background 0.2s", fontFamily: FONT,
                  letterSpacing: "0.04em", minWidth: 110,
                }}
              >
                {loading ? "..." : "Search"}
              </button>
            </div>

            {/* Tier + budget controls */}
            <div style={{ display: "flex", gap: 32, marginTop: 28, flexWrap: "wrap", alignItems: "flex-start" }}>

              {/* Tier counts */}
              <div style={{ flex: 1, minWidth: 300 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
                  <span style={{ fontSize: 12, fontWeight: 800, color: t.textMuted, letterSpacing: "0.1em", textTransform: "uppercase", fontFamily: FONT }}>
                    Results per tier
                  </span>
                  <span style={{ fontSize: 12, fontWeight: 700, color: total > 15 ? "#dc2626" : t.textMuted, fontFamily: FONT }}>
                    {total}/15
                  </span>
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px 32px" }}>
                  {TIER_CONFIG.map(({ key, color, label, desc }) => (
                    <div key={key} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8 }}>
                      <div style={{ minWidth: 0 }}>
                        <span style={{ color, fontWeight: 800, fontSize: 13, fontFamily: FONT }}>{label}</span>
                        <p style={{ color: t.textMuted, fontSize: 11, margin: "1px 0 0", fontFamily: FONT }}>{desc}</p>
                      </div>
                      <CountStepper value={tierCounts[key]} onChange={v => setTierCounts(prev => ({ ...prev, [key]: v }))} t={t} />
                    </div>
                  ))}
                </div>
              </div>

              {/* Budget filter */}
              <div style={{ minWidth: 200 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
                  <button onClick={() => setBudgetEnabled(v => !v)} style={{
                    width: 38, height: 20, borderRadius: 10,
                    background: budgetEnabled ? t.toggleActive : t.toggleTrack,
                    border: "none", cursor: "pointer", position: "relative",
                    transition: "background 0.2s", flexShrink: 0,
                  }}>
                    <div style={{
                      width: 14, height: 14, borderRadius: "50%", background: "#fff",
                      position: "absolute", top: 3, left: budgetEnabled ? 21 : 3,
                      transition: "left 0.2s", boxShadow: "0 1px 3px rgba(0,0,0,0.2)",
                    }} />
                  </button>
                  <span style={{ fontSize: 12, fontWeight: 800, color: t.textMuted, letterSpacing: "0.1em", textTransform: "uppercase", fontFamily: FONT }}>
                    Budget Filter ({currency})
                  </span>
                </div>
                {budgetEnabled && (
                  <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                    <input type="number" placeholder="Min" value={budgetMin} onChange={e => setBudgetMin(e.target.value)}
                      style={{ width: 80, padding: "8px 10px", background: t.inputBg, border: `1px solid ${t.inputBorder}`, borderRadius: 8, color: t.inputColor, fontSize: 13, outline: "none", fontFamily: FONT }} />
                    <span style={{ color: t.textMuted, fontFamily: FONT }}>—</span>
                    <input type="number" placeholder="Max" value={budgetMax} onChange={e => setBudgetMax(e.target.value)}
                      style={{ width: 80, padding: "8px 10px", background: t.inputBg, border: `1px solid ${t.inputBorder}`, borderRadius: 8, color: t.inputColor, fontSize: 13, outline: "none", fontFamily: FONT }} />
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Error */}
          {error && (
            <div style={{
              background: t.errorBg, border: `1px solid ${t.errorBorder}`,
              borderRadius: 10, padding: "12px 18px", marginBottom: 20,
              color: t.errorColor, fontSize: 14, fontFamily: FONT,
              maxWidth: 860, margin: "0 auto 20px",
            }}>
              {error}
            </div>
          )}

          {/* Loading spinner with live status text */}
          {loading && (
            <div style={{ textAlign: "center", padding: "48px 0", animation: "fadeDown 0.3s ease" }}>
              <div style={{
                width: 36, height: 36, borderRadius: "50%",
                border: `3px solid ${t.spinnerTrack}`, borderTopColor: t.spinnerHead,
                animation: "spin 0.7s linear infinite", margin: "0 auto 14px",
              }} />
              <p style={{ color: t.textMuted, fontSize: 14, fontFamily: FONT, margin: 0 }}>
                {status || `Finding alternatives on Amazon ${REGIONS[region].flag}...`}
              </p>
            </div>
          )}

          {/* Results — fade in after box slides up */}
          {hasResults && resultsVisible && (
            <div style={{ animation: "fadeDown 0.35s ease" }}>
              <div style={{ marginBottom: 20 }}>
                <h2 style={{
                  fontSize: 17, fontWeight: 800, margin: "0 0 4px",
                  color: t.textStrong, fontFamily: FONT,
                  overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
                }}>
                  {sortedProducts.length} results · {results.category}
                </h2>
                <p style={{
                  color: t.textMuted, fontSize: 13, margin: 0, fontFamily: FONT,
                  overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
                }}>
                  Amazon {REGIONS[region].flag} · {results.products?.[0]?.title}
                </p>
              </div>

              {/* Flat grid — sorted by tier order, left-to-right */}
              <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
                gap: 16, alignItems: "start",
              }}>
                {sortedProducts.map((product, i) => (
                  <ProductCard key={i} product={product} t={t} index={i} />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}