# components/top_nav.py
from __future__ import annotations
import streamlit as st
from datetime import datetime

def _get_qp(name: str, default: str = "") -> str:
    try:
        v = st.query_params.get(name, default)
        if isinstance(v, list):
            return v[0] if v else default
        return str(v) if v is not None else default
    except Exception:
        return default

def _inject_nav_css():
    st.markdown(
        """
<style>
/* Streamlit 기본 컨텐츠가 상단바에 가리지 않게 */
.main .block-container { padding-top: 92px !important; }

/* (선택) 기본 header 숨김 */
header[data-testid="stHeader"] { display: none !important; }
#MainMenu { visibility: hidden !important; }
footer { visibility: hidden !important; }

/* ====== Top nav ====== */
.tt-nav {
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 72px;
  background: #ffffff;
  z-index: 9999;
  border-bottom: 1px solid rgba(0,0,0,0.08);
  display: flex;
  align-items: center;
}

.tt-nav-inner{
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 18px;
  display: grid;
  grid-template-columns: 220px 1fr 220px;
  align-items: center;
}

/* logo */
.tt-logo {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: #111827;
  font-weight: 700;
  font-size: 18px; /* 더 작게 */
  letter-spacing: -0.2px;
}

/* center menu */
.tt-menu {
  display:flex;
  justify-content:center;
  gap: 20px;
}

/* 메뉴: "글자만" 처럼 보이게 */
.tt-menu a {
  position: relative;
  display:inline-flex;
  align-items:center;
  justify-content:center;
  height: 38px;
  padding: 0 14px;
  border-radius: 0px;
  text-decoration:none;
  color: #6B7280;        /* 기본 회색 */
  font-weight: 600;
  font-size: 14px;
  overflow:hidden;
  transition: color .18s ease;
}

.tt-menu a span{
  position: relative;
  z-index: 2;
}

/* active */
.tt-menu a.active{ color:#111827; }
.tt-menu a.active::before{ transform: translateY(0%); }

/* right area empty */
.tt-right { display:flex; justify-content:flex-end; }

/* ====== Overlay panel (NOT pushing layout) ====== */
.tt-overlay {
  position: fixed;
  top: 72px;
  left: 0; right: 0;
  z-index: 9998;
  pointer-events: none;
}

.tt-overlay .panel-wrap{
  pointer-events: auto;
  width: 100%;
  max-width: 1200px;
  margin: 10px auto 0 auto;
  padding: 0 18px;
  display:flex;
  justify-content:center;
}

.tt-overlay .panel{
  width: min(520px, 92vw);
  background: #ffffff;
  border: 1px solid rgba(0,0,0,0.12);
  border-radius: 14px;
  box-shadow: 0 18px 50px rgba(0,0,0,0.12);
  padding: 16px;
}

.tt-overlay .panel h3{
  margin: 0 0 10px 0;
  font-size: 16px;
  color:#111827;
}

.tt-overlay .panel p, .tt-overlay .panel li{
  color:#374151;
  font-size: 13px;
  line-height: 1.65;
}

.tt-overlay .close-row{
  display:flex;
  justify-content:flex-end;
  margin-top: 12px;
}

.tt-overlay .close-row a{
  text-decoration:none;
  color:#6B7280;
  font-size: 13px;
}

.tt-overlay .close-row a:hover{ color:#111827; }

/* history list */
.tt-history a{
  display:block;
  padding: 10px 10px;
  border-radius: 10px;
  text-decoration:none;
  color:#111827;
}
.tt-history a:hover{
  background: rgba(0,0,0,0.04);
}
.tt-history .meta{
  color:#6B7280;
  font-size:12px;
  margin-top:3px;
}
</style>
        """,
        unsafe_allow_html=True
    )

def render_top_nav(logo_text: str = "TrendTracker"):
    _inject_nav_css()

    menu = _get_qp("menu", "")
    active = menu

    # ✅ 반드시 unsafe_allow_html=True
    st.markdown(
        f"""
<div class="tt-nav">
  <div class="tt-nav-inner">
    <div>
      <a class="tt-logo" href="?">
        <span>🚀</span>
        <span>{logo_text}</span>
      </a>
    </div>

    <div class="tt-menu">
      <a href="?menu=usage" class="{ 'active' if active=='usage' else '' }"><span>사용법</span></a>
      <a href="?menu=api" class="{ 'active' if active=='api' else '' }"><span>API 한도</span></a>
      <a href="?menu=storage" class="{ 'active' if active=='storage' else '' }"><span>데이터 저장 안내</span></a>
      <a href="?menu=history" class="{ 'active' if active=='history' else '' }"><span>검색기록</span></a>
    </div>

    <div class="tt-right"></div>
  </div>
</div>
        """,
        unsafe_allow_html=True
    )

def render_nav_panels(repository, csv_data: str, is_empty: bool):
    menu = _get_qp("menu", "")
    if menu not in ("usage", "api", "storage", "history"):
        return

    st.markdown(
        '<div class="tt-overlay"><div class="panel-wrap"><div class="panel">',
        unsafe_allow_html=True
    )

    if menu == "usage":
        st.markdown(
            """
<h3>📖 사용법</h3>
<ul>
  <li><b>키워드 입력</b>: 검색어 입력 후 Enter 또는 ‘뉴스 검색’</li>
  <li><b>조건</b>: 포함(AND)/제외(NOT)/기간/도메인 등 고급 조건</li>
  <li><b>결과 확인</b>: 기사 목록 + AI 요약/연관키워드 확인</li>
</ul>
            """,
            unsafe_allow_html=True
        )

    elif menu == "api":
        st.markdown(
            """
<h3>📊 API 한도</h3>
<ul>
  <li><b>Tavily</b>: 무료 플랜 기준 월 1,000건 검색 가능</li>
  <li><b>Gemini</b>: 무료 티어 기준 분당 요청 횟수 제한 존재</li>
  <li><b>YouTube Data API</b>: 프로젝트/키 제한 및 쿼터 존재</li>
</ul>
            """,
            unsafe_allow_html=True
        )

    elif menu == "storage":
        st.markdown(
            """
<h3>💾 데이터 저장 안내</h3>
<ul>
  <li>검색 기록은 CSV에 저장됩니다.</li>
  <li>CSV 삭제 시 과거 기록이 사라집니다.</li>
  <li>중요 데이터는 주기적으로 다운로드를 권장합니다.</li>
</ul>
            """,
            unsafe_allow_html=True
        )

    elif menu == "history":
        st.markdown("<h3>📜 검색기록</h3>", unsafe_allow_html=True)

        search_keys = repository.get_all_keys()
        if not search_keys:
            st.markdown("<p>저장된 검색 기록이 없습니다.</p>", unsafe_allow_html=True)
        else:
            keys = list(search_keys)[-15:][::-1]
            st.markdown('<div class="tt-history">', unsafe_allow_html=True)

            for k in keys:
                try:
                    keyword = k.rsplit("-", 1)[0]
                    ts_str = k.rsplit("-", 1)[1]
                    dt = datetime.strptime(ts_str, "%Y%m%d%H%M")
                    meta = dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    keyword = k
                    meta = ""

                st.markdown(
                    f'<a href="?history_key={k}"><div>{keyword}</div><div class="meta">{meta}</div></a>',
                    unsafe_allow_html=True
                )

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        if is_empty:
            st.button("📥 CSV 다운로드", disabled=True, key="nav_dl_disabled")
        else:
            st.download_button(
                label="📥 CSV 다운로드",
                data=csv_data,
                file_name=f"trendtracker_export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key="nav_download_btn",
            )

    st.markdown('<div class="close-row"><a href="?">닫기 ✕</a></div>', unsafe_allow_html=True)
    st.markdown('</div></div></div>', unsafe_allow_html=True)
