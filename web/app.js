(function () {
  const payload = window.UNIVERSITY_DATA || { universities: [] };
  const universities = payload.universities || [];
  const state = {
    query: "",
    selected: null,
    activeIndex: -1,
    activeType: "전체",
  };

  const searchInput = document.getElementById("searchInput");
  const suggestions = document.getElementById("suggestions");
  const detail = document.getElementById("detail");
  const empty = document.getElementById("empty");

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function normalize(value) {
    return String(value || "").replace(/\s+/g, "").toLowerCase();
  }

  function admissionsOf(university) {
    return university?.structured_admissions || [];
  }

  function hasReliableValue(value) {
    const text = String(value || "").trim();
    return Boolean(text);
  }

  const ambiguousCsaveCnatValues = new Set([
    "적용",
    "있음",
    "적용 가능",
    "일부 모집단위 적용",
    "의·약 계열 일부 적용",
    "의/약 일부 적용",
    "의/치/약 일부 적용",
    "의/치/약/간 일부 적용",
    "의/치/약/수 일부 적용",
    "의예 등 일부 모집단위 적용",
    "치의예 계열 기준 적용",
    "약학 일부 적용",
    "간호 일부 적용",
  ]);

  function needsCsaveCnatReview(value) {
    const text = String(value || "").trim();
    return ambiguousCsaveCnatValues.has(text) || /일부 적용$/.test(text) || text.includes("확인 필요");
  }

  function getMatches() {
    const query = normalize(state.query);
    if (!query) return [];

    return universities
      .filter(university => {
        const terms = [university.name, university.base_name, university.campus, ...(university.search_terms || [])];
        return terms.some(term => normalize(term).includes(query));
      })
      .sort((a, b) => {
        const aName = normalize(a.name);
        const bName = normalize(b.name);
        const aStarts = aName.startsWith(query) ? 0 : 1;
        const bStarts = bName.startsWith(query) ? 0 : 1;
        return aStarts - bStarts || a.name.localeCompare(b.name, "ko");
      })
      .slice(0, 10);
  }

  function selectUniversity(university) {
    state.selected = university;
    state.query = university.name;
    state.activeIndex = -1;
    state.activeType = "전체";
    searchInput.value = university.name;
    renderSuggestions([]);
    renderDetail(university);
  }

  function renderSuggestions(matches = getMatches()) {
    if (!matches.length) {
      suggestions.classList.add("hidden");
      suggestions.innerHTML = "";
      return;
    }

    suggestions.classList.remove("hidden");
    suggestions.innerHTML = matches.map((university, index) => {
      const admissions = admissionsOf(university);
      const status = admissions.length ? `정리된 전형 ${admissions.length}개` : "상세 전형 보류";
      return `
        <button class="suggestion ${index === state.activeIndex ? "active" : ""}" type="button" data-index="${index}">
          <strong>${escapeHtml(university.name)}</strong>
          <span>${escapeHtml(university.region || "지역 미표기")} · ${escapeHtml(status)}</span>
        </button>
      `;
    }).join("");

    suggestions.querySelectorAll("[data-index]").forEach(button => {
      button.addEventListener("mousedown", event => {
        event.preventDefault();
        selectUniversity(matches[Number(button.dataset.index)]);
      });
    });
  }

  function renderDetail(university) {
    const admissions = admissionsOf(university);
    const types = ["전체", ...new Set(admissions.map(entry => entry.admission_type || "전형"))];
    if (!types.includes(state.activeType)) state.activeType = "전체";
    const visibleAdmissions = state.activeType === "전체"
      ? admissions
      : admissions.filter(entry => (entry.admission_type || "전형") === state.activeType);
    empty.classList.add("hidden");
    detail.classList.remove("hidden");

    if (!admissions.length) {
      detail.innerHTML = `
        <div class="detail-head">
          <div>
            <h2>${escapeHtml(university.name)}</h2>
          </div>
          <div class="detail-meta">${escapeHtml(university.region || "지역 미표기")}</div>
        </div>
        <div class="empty">이 대학은 확실하게 정리된 전형 정보가 없어 표시하지 않았습니다.</div>
      `;
      return;
    }

    detail.innerHTML = `
      <div class="detail-head">
        <div>
          <h2>${escapeHtml(university.name)}</h2>
        </div>
        <div class="detail-meta">${escapeHtml(university.region || "지역 미표기")} · 정리된 전형 ${admissions.length.toLocaleString("ko-KR")}개</div>
      </div>
      <div class="tabs">
        ${types.map(type => `
          <button class="tab ${state.activeType === type ? "active" : ""}" type="button" data-type="${escapeHtml(type)}">
            ${escapeHtml(type)} ${type === "전체" ? admissions.length : admissions.filter(entry => (entry.admission_type || "전형") === type).length}
          </button>
        `).join("")}
      </div>
      <div class="admissions">
        ${visibleAdmissions.map(entry => renderAdmission(entry)).join("")}
      </div>
    `;

    detail.querySelectorAll("[data-type]").forEach(button => {
      button.addEventListener("click", () => {
        state.activeType = button.dataset.type;
        renderDetail(university);
      });
    });
  }

  function renderAdmission(entry) {
    const facts = [
      ["모집인원", entry.capacity],
      ["전형방법", entry.method],
      ["수능최저", entry.csat_minimum],
    ].filter(([, value]) => hasReliableValue(value));

    return `
      <article class="admission">
        <div class="admission-type">${escapeHtml(entry.admission_type || "전형")}</div>
        <div class="admission-main">
          <h3>${escapeHtml(entry.track_name || "전형명 미표기")}</h3>
          ${needsCsaveCnatReview(entry.csat_minimum) ? `<div class="warning">수능최저 확인 필요: 과목/개수/합산 기준 보완 필요</div>` : ""}
          <div class="facts">
            ${facts.map(([label, value]) => `
              <div class="fact">
                <small>${escapeHtml(label)}</small>
                <div>${escapeHtml(value)}</div>
              </div>
            `).join("")}
          </div>
          ${entry.notes ? `<div class="note">${escapeHtml(entry.notes)}</div>` : ""}
        </div>
      </article>
    `;
  }

  searchInput.addEventListener("input", event => {
    state.query = event.target.value;
    state.selected = null;
    state.activeIndex = -1;
    const matches = getMatches();
    renderSuggestions(matches);

    if (!state.query.trim()) {
      detail.classList.add("hidden");
      empty.classList.add("hidden");
    } else if (!matches.length) {
      detail.classList.add("hidden");
      empty.classList.add("hidden");
    } else {
      detail.classList.add("hidden");
      empty.classList.add("hidden");
    }
  });

  searchInput.addEventListener("keydown", event => {
    const matches = getMatches();
    if (!matches.length) return;

    if (event.key === "ArrowDown") {
      event.preventDefault();
      state.activeIndex = Math.min(state.activeIndex + 1, matches.length - 1);
      renderSuggestions(matches);
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();
      state.activeIndex = Math.max(state.activeIndex - 1, 0);
      renderSuggestions(matches);
    }

    if (event.key === "Enter") {
      if (event.isComposing || event.keyCode === 229) return;
      event.preventDefault();
      const index = state.activeIndex >= 0 ? state.activeIndex : 0;
      selectUniversity(matches[index]);
    }

    if (event.key === "Escape") {
      state.activeIndex = -1;
      renderSuggestions([]);
    }
  });

  searchInput.addEventListener("keyup", event => {
    if (event.key !== "Enter" || event.isComposing || event.keyCode === 229) return;
    window.setTimeout(() => {
      const matches = getMatches();
      if (!state.selected && matches.length) {
        selectUniversity(matches[0]);
      }
    }, 0);
  });

  document.addEventListener("click", event => {
    if (!event.target.closest(".search-wrap")) {
      renderSuggestions([]);
    }
  });
})();
