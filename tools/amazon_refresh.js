// 아마존 상품 목록 갱신 수집기 — Claude 데스크톱 앱 내장 브라우저에서 amazon.com 페이지를 연 상태로 실행.
// 1) 이 파일 내용을 javascript_tool로 실행 → 'started'
// 2) 45초마다 `window.__rf.status()` 로 진행 확인 → done:true 가 될 때까지
// 3) `window.__rf.chunk(0)`, `chunk(1)`, ... (null 나올 때까지) 결과를 받는다 (각 결과는 파일로 저장됨)
(() => {
  document.cookie = "i18n-prefs=USD; domain=.amazon.com; path=/";
  document.cookie = "lc-main=en_US; domain=.amazon.com; path=/";
  const CATS = {
    "skincare": "/gp/bestsellers/beauty/11060451",
    "haircare": "/gp/bestsellers/beauty/11057241",
    "beauty-tools": "/gp/bestsellers/beauty/11062741",
    "kitchen": "/gp/bestsellers/kitchen/289913",
    "kitchen-tools": "/gp/bestsellers/kitchen/289754",
    "storage": "/gp/bestsellers/home-garden/3610841",
    "fitness": "/gp/bestsellers/sporting-goods/3407731",
    "pet": "/gp/bestsellers/pet-supplies",
    "baby": "/gp/bestsellers/baby-products",
  };
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const st = { phase: "start", done: false, targets: 0, fetched: 0, results: [], errors: 0 };
  async function detail(a, c) {
    const r = await fetch("/dp/" + a + "?language=en_US&currency=USD", { credentials: "include" });
    const t = await r.text();
    const d = new DOMParser().parseFromString(t, "text/html");
    const q = s => d.querySelector(s);
    const ti = q("#productTitle");
    if (!ti) return { asin: a, category: c, dead: r.status === 404 || t.includes("couldn't find that page"), status: r.status };
    const bullets = [...d.querySelectorAll("#feature-bullets li span.a-list-item, #productFactsDesktopExpander li span.a-list-item")]
      .map(x => x.textContent.trim().replace(/\s+/g, " ")).filter(x => x.length > 15).slice(0, 6).map(x => x.slice(0, 200));
    const img = q("#landingImage");
    return {
      asin: a, category: c,
      title: ti.textContent.trim().replace(/\s+/g, " ").slice(0, 150),
      price: ((q("#corePrice_feature_div .a-offscreen") || q(".a-price .a-offscreen") || {}).textContent || "").trim(),
      rating: ((q("#acrPopover .a-icon-alt") || {}).textContent || "").trim(),
      review_count: ((q("#acrCustomerReviewText") || {}).textContent || "").replace(/[()]/g, "").trim(),
      features: bullets,
      image: img ? (img.getAttribute("data-old-hires") || img.src) : "",
    };
  }
  (async () => {
    const targets = new Map();
    try {
      const cur = await (await fetch("https://raw.githubusercontent.com/Follow-Refer/autoblog/main/products.json", { cache: "no-store" })).json();
      for (const p of cur.products) targets.set(p.asin, p.category);
    } catch (e) { st.errors++; }
    st.phase = "bestsellers";
    for (const [c, u] of Object.entries(CATS)) {
      try {
        const t = await (await fetch(u, { credentials: "include" })).text();
        [...new Set([...t.matchAll(/data-asin="(B0[A-Z0-9]{8})"/g)].map(m => m[1]))].slice(0, 20)
          .forEach(a => { if (!targets.has(a)) targets.set(a, c); });
      } catch (e) { st.errors++; }
      await sleep(700);
    }
    st.phase = "details"; st.targets = targets.size;
    for (const [a, c] of targets) {
      try { st.results.push(await detail(a, c)); } catch (e) { st.errors++; st.results.push({ asin: a, category: c, error: String(e) }); }
      st.fetched++;
      await sleep(400);
    }
    st.phase = "done"; st.done = true;
  })();
  window.__rf = {
    status: () => ({ phase: st.phase, done: st.done, targets: st.targets, fetched: st.fetched, errors: st.errors }),
    chunk: i => {
      const part = st.results.slice(i * 40, i * 40 + 40);
      return part.length ? JSON.stringify(part) + " ".repeat(60000) : null;
    },
  };
  return "started";
})();
