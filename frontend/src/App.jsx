import { useState } from "react";

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

const THEME = {
  light: {
    pageBg:          "#f4f6f9",
    navBg:           "#ffffff",
    navBorder:       "#e8ecf0",
    cardBg:          "#ffffff",
    cardBorder:      "#e8ecf0",
    boxBg:           "#ffffff",
    boxBorder:       "#e8ecf0",
    inputBg:         "#f8fafc",
    inputBorder:     "#e2e8f0",
    inputColor:      "#0f172a",
    toggleTrack:     "#e2e8f0",
    toggleActive:    "#0f172a",
    btnBg:           "#0f172a",
    btnColor:        "#ffffff",
    btnDisabled:     "#e2e8f0",
    text:            "#1e293b",
    textMuted:       "#94a3b8",
    textStrong:      "#0f172a",
    stepperBg:       "#f1f5f9",
    stepperBorder:   "#e2e8f0",
    stepperColor:    "#64748b",
    regionBg:        "#f1f5f9",
    regionBorder:    "#e2e8f0",
    regionActive:    "#ffffff",
    regionShadow:    "0 1px 3px rgba(0,0,0,0.08)",
    shadow:          "0 2px 12px rgba(0,0,0,0.05)",
    cardShadow:      "0 1px 4px rgba(0,0,0,0.06)",
    cardHoverShadow: "0 8px 24px rgba(0,0,0,0.10)",
    imageBg:         "#f8fafc",
    imageBorder:     "#f1f5f9",
    divider:         "#f1f5f9",
    errorBg:         "#fef2f2",
    errorBorder:     "#fecaca",
    errorColor:      "#dc2626",
    spinnerTrack:    "#e2e8f0",
    spinnerHead:     "#0f172a",
    modeIcon:        "🌙",
  },
  dark: {
    pageBg:          "#0a0f1a",
    navBg:           "#0f172a",
    navBorder:       "#1e293b",
    cardBg:          "#0f172a",
    cardBorder:      "#1e293b",
    boxBg:           "#0f172a",
    boxBorder:       "#1e293b",
    inputBg:         "#1e293b",
    inputBorder:     "#334155",
    inputColor:      "#f1f5f9",
    toggleTrack:     "#334155",
    toggleActive:    "#60a5fa",
    btnBg:           "#3b82f6",
    btnColor:        "#ffffff",
    btnDisabled:     "#1e293b",
    text:            "#cbd5e1",
    textMuted:       "#475569",
    textStrong:      "#f1f5f9",
    stepperBg:       "#1e293b",
    stepperBorder:   "#334155",
    stepperColor:    "#94a3b8",
    regionBg:        "#1e293b",
    regionBorder:    "#334155",
    regionActive:    "#334155",
    regionShadow:    "0 1px 3px rgba(0,0,0,0.3)",
    shadow:          "0 2px 16px rgba(0,0,0,0.3)",
    cardShadow:      "0 1px 4px rgba(0,0,0,0.3)",
    cardHoverShadow: "0 8px 28px rgba(0,0,0,0.5)",
    imageBg:         "#1e293b",
    imageBorder:     "#334155",
    divider:         "#1e293b",
    errorBg:         "#2d0a0a",
    errorBorder:     "#7f1d1d",
    errorColor:      "#fca5a5",
    spinnerTrack:    "#1e293b",
    spinnerHead:     "#60a5fa",
    modeIcon:        "☀️",
  },
};

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
      fontSize: 11, fontWeight: 700,
      letterSpacing: "0.06em", textTransform: "uppercase",
      fontFamily: "'Courier New', monospace", whiteSpace: "nowrap",
    }}>
      {s.label}
    </span>
  );
}

function CountStepper({ value, onChange, t }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
      <button onClick={() => onChange(Math.max(0, value - 1))} style={{
        width: 26, height: 26, borderRadius: 6,
        background: t.stepperBg, border: `1px solid ${t.stepperBorder}`,
        color: t.stepperColor, cursor: "pointer", fontSize: 15, fontWeight: 700,
        display: "flex", alignItems: "center", justifyContent: "center",
        transition: "background 0.15s"
      }}>−</button>
      <span style={{
        width: 22, textAlign: "center",
        color: t.textStrong, fontWeight: 800, fontSize: 14,
        fontFamily: "'Courier New', monospace"
      }}>{value}</span>
      <button onClick={() => onChange(Math.min(10, value + 1))} style={{
        width: 26, height: 26, borderRadius: 6,
        background: t.stepperBg, border: `1px solid ${t.stepperBorder}`,
        color: t.stepperColor, cursor: "pointer", fontSize: 15, fontWeight: 700,
        display: "flex", alignItems: "center", justifyContent: "center",
        transition: "background 0.15s"
      }}>+</button>
    </div>
  );
}

function ProductCard({ product, t }) {
  const imageUrl = typeof product.image === "object" ? product.image?.link : product.image;
  const merchant = product.merchants?.[0];
  const s = TIER_STYLES[product.tier] || TIER_STYLES.original;
  const isDark = t === THEME.dark;

  return (
    <div
      style={{
        background: t.cardBg, border: `1px solid ${t.cardBorder}`,
        borderRadius: 16, overflow: "hidden",
        boxShadow: t.cardShadow,
        transition: "box-shadow 0.2s, transform 0.2s, border-color 0.2s",
        display: "flex", flexDirection: "column",
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
      <div style={{ height: 4, background: s.color, opacity: 0.8 }} />

      <div style={{
        height: 160, background: t.imageBg,
        display: "flex", alignItems: "center", justifyContent: "center",
        borderBottom: `1px solid ${t.imageBorder}`, padding: 8
      }}>
        {imageUrl
          ? <img src={imageUrl} alt={product.title} style={{ maxHeight: "100%", maxWidth: "100%", objectFit: "contain" }} />
          : <div style={{ color: t.textMuted, fontSize: 28 }}>📦</div>
        }
      </div>

      <div style={{ padding: "14px 16px 16px", flex: 1, display: "flex", flexDirection: "column" }}>
        <div style={{ marginBottom: 8 }}>
          <TierBadge tier={product.tier} t={t} />
        </div>

        <p style={{
          color: t.text, fontSize: 13, fontWeight: 500,
          lineHeight: 1.45, margin: "0 0 auto", paddingBottom: 12,
          display: "-webkit-box", WebkitLineClamp: 2,
          WebkitBoxOrient: "vertical", overflow: "hidden",
          fontFamily: "Georgia, serif",
        }}>
          {product.title}
        </p>

        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 12 }}>
          <div>
            <span style={{ color: t.textStrong, fontWeight: 800, fontSize: 17, fontFamily: "'Courier New', monospace" }}>
              {merchant?.price != null ? `$${merchant.price.toFixed(2)}` : "—"}
            </span>
            {merchant?.merchant && (
              <span style={{ color: t.textMuted, fontSize: 11, marginLeft: 6 }}>{merchant.merchant}</span>
            )}
          </div>
          {merchant?.affiliate_link && (
            <a href={merchant.affiliate_link} target="_blank" rel="noopener noreferrer"
              style={{
                background: t.btnBg, color: t.btnColor,
                padding: "7px 14px", borderRadius: 8,
                fontSize: 12, fontWeight: 700, textDecoration: "none",
                transition: "opacity 0.15s", letterSpacing: "0.03em"
              }}
              onMouseEnter={e => e.currentTarget.style.opacity = "0.85"}
              onMouseLeave={e => e.currentTarget.style.opacity = "1"}
            >
              View →
            </a>
          )}
        </div>

        {product.merchants?.length > 1 && (
          <div style={{ marginTop: 10, paddingTop: 10, borderTop: `1px solid ${t.divider}` }}>
            {product.merchants.slice(1).map(m => (
              <div key={m.merchant} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                <span style={{ color: t.textMuted, fontSize: 12 }}>{m.merchant}</span>
                <a href={m.affiliate_link} target="_blank" rel="noopener noreferrer"
                  style={{ color: "#3b82f6", fontSize: 12, fontWeight: 600 }}>
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

function TierSection({ tier, products, t }) {
  const s = TIER_STYLES[tier] || TIER_STYLES.original;
  const isDark = t === THEME.dark;
  if (!products.length) return null;
  return (
    <div style={{ marginBottom: 36 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 16 }}>
        <div style={{ width: 4, height: 22, borderRadius: 2, background: s.color }} />
        <h3 style={{
          margin: 0, fontSize: 15, fontWeight: 800, color: s.color,
          letterSpacing: "0.08em", textTransform: "uppercase",
          fontFamily: "'Courier New', monospace"
        }}>
          {s.label}
        </h3>
        <span style={{
          background: isDark ? s.darkBg : s.lightBg,
          color: s.color,
          border: `1px solid ${isDark ? s.darkBorder : s.lightBorder}`,
          borderRadius: 20, padding: "1px 8px", fontSize: 11, fontWeight: 700,
          fontFamily: "'Courier New', monospace"
        }}>
          {products.length}
        </span>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(210px, 1fr))", gap: 14 }}>
        {products.map((p, i) => <ProductCard key={i} product={p} t={t} />)}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main App
// ---------------------------------------------------------------------------

export default function App() {
  const [darkMode, setDarkMode]           = useState(false);
  const [query, setQuery]                 = useState("");
  const [region, setRegion]               = useState("CA");
  const [budgetEnabled, setBudgetEnabled] = useState(false);
  const [budgetMin, setBudgetMin]         = useState("");
  const [budgetMax, setBudgetMax]         = useState("");
  const [tierCounts, setTierCounts]       = useState({ count_budget: 1, count_mid: 2, count_premium: 1, count_next_gen: 1 });
  const [results, setResults]             = useState(null);
  const [loading, setLoading]             = useState(false);
  const [error, setError]                 = useState(null);

  const t        = darkMode ? THEME.dark : THEME.light;
  const total    = Object.values(tierCounts).reduce((a, b) => a + b, 0);
  const currency = REGIONS[region].currency;

  const handleSearch = async () => {
    if (!query.trim()) return;
    if (total === 0) { setError("Select at least 1 substitute"); return; }
    if (total > 15)  { setError("Maximum 15 total substitutes"); return; }

    setLoading(true);
    setError(null);
    setResults(null);

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
      if (!res.ok) { const e = await res.json(); throw new Error(e.detail || "Search failed"); }
      setResults(await res.json());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const grouped = results ? {
    original:   results.products?.filter(p => p.tier === "original")  || [],
    budget:     results.products?.filter(p => p.tier === "budget")    || [],
    mid:        results.products?.filter(p => p.tier === "mid")       || [],
    premium:    results.products?.filter(p => p.tier === "premium")   || [],
    "next-gen": results.products?.filter(p => p.tier === "next-gen")  || [],
  } : {};

  return (
    <div style={{
      minHeight: "100vh",
      background: t.pageBg,
      color: t.text,
      fontFamily: "Georgia, 'Times New Roman', serif",
      transition: "background 0.3s, color 0.3s"
    }}>

      {/* ── Navbar ── */}
      <div style={{
        background: t.navBg,
        borderBottom: `1px solid ${t.navBorder}`,
        padding: "0 24px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        height: 60,
        boxShadow: "0 1px 3px rgba(0,0,0,0.04)",
        position: "sticky",
        top: 0,
        zIndex: 100,
        transition: "background 0.3s, border-color 0.3s",
      }}>

        {/* Left — dark mode toggle */}
        <button
          onClick={() => setDarkMode(d => !d)}
          title={darkMode ? "Switch to light mode" : "Switch to dark mode"}
          style={{
            width: 38, height: 38, borderRadius: 10,
            background: t.stepperBg, border: `1px solid ${t.stepperBorder}`,
            cursor: "pointer", fontSize: 17,
            display: "flex", alignItems: "center", justifyContent: "center",
            transition: "background 0.2s, border-color 0.2s",
            flexShrink: 0,
          }}
          onMouseEnter={e => e.currentTarget.style.background = t.regionBorder}
          onMouseLeave={e => e.currentTarget.style.background = t.stepperBg}
        >
          {t.modeIcon}
        </button>

        {/* Center — title (absolutely centered in navbar) */}
        <div style={{
          position: "absolute",
          left: "50%",
          transform: "translateX(-50%)",
          display: "flex",
          alignItems: "baseline",
          gap: 8,
          pointerEvents: "none",
        }}>
          <span style={{
            fontSize: 22, fontWeight: 900, color: t.textStrong,
            letterSpacing: "-0.02em", fontFamily: "'Courier New', monospace"
          }}>
            BuyBuzz
          </span>
          <span style={{ fontSize: 12, color: t.textMuted, fontFamily: "Georgia, serif" }}>
            product alternatives
          </span>
        </div>

        {/* Right — region toggle */}
        <div style={{
          display: "flex", background: t.regionBg,
          borderRadius: 10, padding: 3, gap: 2,
          border: `1px solid ${t.regionBorder}`,
          flexShrink: 0,
        }}>
          {Object.entries(REGIONS).map(([key, r]) => (
            <button key={key} onClick={() => setRegion(key)} style={{
              padding: "6px 14px", borderRadius: 8, border: "none",
              background: region === key ? t.regionActive : "transparent",
              color: region === key ? t.textStrong : t.textMuted,
              fontWeight: region === key ? 700 : 500,
              fontSize: 13, cursor: "pointer",
              boxShadow: region === key ? t.regionShadow : "none",
              transition: "all 0.15s", fontFamily: "Georgia, serif"
            }}>
              {r.label}
            </button>
          ))}
        </div>
      </div>

      {/* ── Main content ── */}
      <div style={{
        maxWidth: 1140,
        margin: "0 auto",
        padding: results ? "24px 24px 40px" : "64px 24px 40px",
        transition: "padding 0.4s ease"
      }}>

        {/* Search box — centered, max width 860 */}
        <div style={{
          background: t.boxBg, borderRadius: 20,
          border: `1px solid ${t.boxBorder}`,
          boxShadow: t.shadow, padding: "32px 36px",
          maxWidth: 860, margin: "0 auto 32px",
          transition: "background 0.3s, border-color 0.3s"
        }}>
          <p style={{ margin: "0 0 14px", fontSize: 13, color: t.textMuted }}>
            Paste an Amazon URL or type a product name
          </p>

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
                outline: "none", transition: "border-color 0.2s",
                fontFamily: "Georgia, serif"
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
                fontWeight: 700, fontSize: 14,
                cursor: loading || !query.trim() ? "not-allowed" : "pointer",
                opacity: total === 0 ? 0.4 : 1,
                transition: "background 0.2s",
                fontFamily: "'Courier New', monospace",
                letterSpacing: "0.04em", minWidth: 110
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
                <span style={{
                  fontSize: 12, fontWeight: 700, color: t.textMuted,
                  letterSpacing: "0.1em", textTransform: "uppercase",
                  fontFamily: "'Courier New', monospace"
                }}>
                  Results per tier
                </span>
                <span style={{
                  fontSize: 12, fontWeight: 700,
                  color: total > 15 ? "#dc2626" : t.textMuted,
                  fontFamily: "'Courier New', monospace"
                }}>
                  {total}/15
                </span>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px 32px" }}>
                {TIER_CONFIG.map(({ key, color, label, desc }) => (
                  <div key={key} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8 }}>
                    <div>
                      <span style={{ color, fontWeight: 700, fontSize: 13, fontFamily: "'Courier New', monospace" }}>{label}</span>
                      <p style={{ color: t.textMuted, fontSize: 11, margin: "1px 0 0" }}>{desc}</p>
                    </div>
                    <CountStepper
                      value={tierCounts[key]}
                      onChange={v => setTierCounts(prev => ({ ...prev, [key]: v }))}
                      t={t}
                    />
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
                  transition: "background 0.2s", flexShrink: 0
                }}>
                  <div style={{
                    width: 14, height: 14, borderRadius: "50%", background: "#fff",
                    position: "absolute", top: 3,
                    left: budgetEnabled ? 21 : 3,
                    transition: "left 0.2s",
                    boxShadow: "0 1px 3px rgba(0,0,0,0.2)"
                  }} />
                </button>
                <span style={{
                  fontSize: 12, fontWeight: 700, color: t.textMuted,
                  letterSpacing: "0.1em", textTransform: "uppercase",
                  fontFamily: "'Courier New', monospace"
                }}>
                  Budget Filter ({currency})
                </span>
              </div>
              {budgetEnabled && (
                <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                  <input type="number" placeholder="Min"
                    value={budgetMin} onChange={e => setBudgetMin(e.target.value)}
                    style={{
                      width: 80, padding: "8px 10px",
                      background: t.inputBg, border: `1px solid ${t.inputBorder}`,
                      borderRadius: 8, color: t.inputColor, fontSize: 13,
                      outline: "none", fontFamily: "Georgia, serif"
                    }} />
                  <span style={{ color: t.textMuted }}>—</span>
                  <input type="number" placeholder="Max"
                    value={budgetMax} onChange={e => setBudgetMax(e.target.value)}
                    style={{
                      width: 80, padding: "8px 10px",
                      background: t.inputBg, border: `1px solid ${t.inputBorder}`,
                      borderRadius: 8, color: t.inputColor, fontSize: 13,
                      outline: "none", fontFamily: "Georgia, serif"
                    }} />
                </div>
              )}
            </div>
          </div>
        </div>

        {/* ── Results area ── */}
        <div style={{ maxWidth: 1140, margin: "0 auto" }}>

          {error && (
            <div style={{
              background: t.errorBg, border: `1px solid ${t.errorBorder}`,
              borderRadius: 10, padding: "12px 18px", marginBottom: 20,
              color: t.errorColor, fontSize: 14
            }}>
              {error}
            </div>
          )}

          {loading && (
            <div style={{ textAlign: "center", padding: "64px 0" }}>
              <div style={{
                width: 36, height: 36, borderRadius: "50%",
                border: `3px solid ${t.spinnerTrack}`,
                borderTopColor: t.spinnerHead,
                animation: "spin 0.7s linear infinite",
                margin: "0 auto 16px"
              }} />
              <p style={{ color: t.textMuted, fontSize: 14 }}>
                Finding alternatives on Amazon {REGIONS[region].flag}...
              </p>
              <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
            </div>
          )}

          {results && !loading && (
            <div>
              <div style={{ marginBottom: 28 }}>
                <h2 style={{
                  fontSize: 18, fontWeight: 800, margin: "0 0 4px",
                  color: t.textStrong, fontFamily: "'Courier New', monospace"
                }}>
                  {results.products?.length} results for "{results.products?.[0]?.title}"
                </h2>
                <p style={{ color: t.textMuted, fontSize: 13, margin: 0 }}>
                  {results.category} · Amazon {REGIONS[region].flag}
                </p>
              </div>

              <TierSection tier="original" products={grouped.original   || []} t={t} />
              <TierSection tier="budget"   products={grouped.budget     || []} t={t} />
              <TierSection tier="mid"      products={grouped.mid        || []} t={t} />
              <TierSection tier="premium"  products={grouped.premium    || []} t={t} />
              <TierSection tier="next-gen" products={grouped["next-gen"]|| []} t={t} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}