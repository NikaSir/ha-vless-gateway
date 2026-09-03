// VLESS Gateway panel scaffold for Home Assistant NikaS.
// Domain telemetry is bound only through panel.config.entity_roles. This file
// intentionally contains no guessed Home Assistant entity IDs or commands.

const VLESS_APP = {
  title: "VLESS Gateway",
  uiVersion: "0.1.1",
  domain: "vless_gateway",
  preferredView: "overview",
  tabs: [
    ["overview", "mdi:view-dashboard-outline", "Обзор"],
    ["routes", "mdi:routes", "Маршруты"],
    ["traffic", "mdi:chart-areaspline", "Трафик"],
    ["diagnostics", "mdi:stethoscope", "Диагн."],
  ],
};

const SAFE_DEFAULT_ROUTE = "/dashboard-infrastructure/overview";
const TONES = new Set(["ok", "active", "warn", "bad", "unknown"]);
const INVALID_STATES = new Set(["", "unknown", "unavailable", "none", "null"]);

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function validEntityId(value) {
  return typeof value === "string" && /^[a-z0-9_]+\.[a-z0-9_]+$/.test(value);
}

function versionLine(value) {
  const normalized = String(value ?? "")
    .trim()
    .replace(/^UI\s+v/i, "")
    .replace(/^v/i, "");
  return /^\d+\.\d+\.\d+$/.test(normalized)
    ? `UI v${normalized}`
    : `UI v${VLESS_APP.uiVersion}`;
}

function sameTreeShape(current, desired) {
  if (!current || !desired || current.nodeType !== desired.nodeType) return false;
  if (current.nodeType === Node.ELEMENT_NODE && current.tagName !== desired.tagName) return false;
  if (current.childNodes.length !== desired.childNodes.length) return false;
  for (let index = 0; index < current.childNodes.length; index += 1) {
    if (!sameTreeShape(current.childNodes[index], desired.childNodes[index])) return false;
  }
  return true;
}

function syncTree(current, desired) {
  if (current.nodeType === Node.TEXT_NODE || current.nodeType === Node.COMMENT_NODE) {
    if (current.nodeValue !== desired.nodeValue) current.nodeValue = desired.nodeValue;
    return;
  }
  if (current.nodeType === Node.ELEMENT_NODE) {
    for (const attribute of [...current.attributes]) {
      if (!desired.hasAttribute(attribute.name)) current.removeAttribute(attribute.name);
    }
    for (const attribute of [...desired.attributes]) {
      if (current.getAttribute(attribute.name) !== attribute.value) {
        current.setAttribute(attribute.name, attribute.value);
      }
    }
  }
  for (let index = 0; index < current.childNodes.length; index += 1) {
    syncTree(current.childNodes[index], desired.childNodes[index]);
  }
}

function commitStableMarkup(root, markup) {
  const template = document.createElement("template");
  template.innerHTML = markup;
  const current = [...root.childNodes];
  const desired = [...template.content.childNodes];
  const compatible = current.length === desired.length
    && current.every((node, index) => sameTreeShape(node, desired[index]));
  if (!compatible) {
    root.replaceChildren(template.content.cloneNode(true));
    return true;
  }
  current.forEach((node, index) => syncTree(node, desired[index]));
  return false;
}

function formatTimestamp(value, locale = "ru") {
  if (!value) return "Нет данных";
  const timestamp = Date.parse(value);
  if (!Number.isFinite(timestamp)) return String(value);
  return new Intl.DateTimeFormat(locale, {
    day: "2-digit",
    month: "2-digit",
    year: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(new Date(timestamp));
}

function diagnosticValue(value) {
  if (value === undefined || value === null) return "Нет данных";
  if (["string", "number", "boolean"].includes(typeof value)) return String(value);
  try {
    return JSON.stringify(value);
  } catch (_error) {
    return String(value);
  }
}

class VlessGatewayPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._panel = null;
    this._activeView = VLESS_APP.preferredView;
    this._loading = true;
    this._shellMounted = false;
    this._renderQueued = false;
    this._returnRoute = null;
    this._visitedViews = new Map();
    this._registryEntityIds = [];
    this._registryLoaded = false;
    this._registryLoading = false;
    this._registryError = null;
    this._connected = false;
    this._scrollGuardCleanup = null;
  }

  set hass(value) {
    this._hass = value;
    this._loading = false;
    this._queueRender();
    if (!this._registryLoaded && !this._registryLoading) this._loadRegistry();
  }

  get hass() {
    return this._hass;
  }

  set panel(value) {
    this._panel = value;
    const preferred = value?.config?.preferred_view || VLESS_APP.preferredView;
    this._activeView = this._validViews().has(preferred) ? preferred : VLESS_APP.preferredView;
    this._registryLoaded = false;
    this._queueRender();
    if (this._hass && !this._registryLoading) this._loadRegistry();
  }

  get panel() {
    return this._panel;
  }

  connectedCallback() {
    this._connected = true;
    this._bindShellBoundaryGuard();
    this._queueRender();
  }

  disconnectedCallback() {
    this._connected = false;
    this._scrollGuardCleanup?.();
    this._scrollGuardCleanup = null;
  }

  _config() {
    const rawTabs = this._panel?.config?.tabs;
    const tabs = Array.isArray(rawTabs)
      ? rawTabs.filter((tab) => Array.isArray(tab) && tab.length >= 3).slice(0, 5)
      : VLESS_APP.tabs;
    return {
      title: this._panel?.config?.title || VLESS_APP.title,
      versionLine: versionLine(this._panel?.config?.ui_version || VLESS_APP.uiVersion),
      tabs: tabs.length >= 3 ? tabs : VLESS_APP.tabs,
    };
  }

  _validViews() {
    return new Set(this._config().tabs.map(([view]) => view));
  }

  _entityRoles() {
    const raw = this._panel?.config?.entity_roles;
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) return {};
    return Object.fromEntries(
      Object.entries(raw).filter(([, entityId]) => validEntityId(entityId)),
    );
  }

  _roleEntityId(role) {
    return this._entityRoles()[role] || null;
  }

  _tone(value) {
    return TONES.has(value) ? value : "unknown";
  }

  _stateTone(rawState) {
    const value = String(rawState ?? "").toLowerCase();
    if (value === "unavailable") return "bad";
    if (INVALID_STATES.has(value)) return "unknown";
    if (["on", "ok", "healthy", "connected", "running", "active", "ready", "home"].includes(value)) {
      return "ok";
    }
    if (["warning", "warn", "degraded", "slow", "standby", "reconnecting"].includes(value)) {
      return "warn";
    }
    if (["off", "error", "failed", "fault", "disconnected", "blocked", "stopped"].includes(value)) {
      return "bad";
    }
    return "active";
  }

  _displayState(state) {
    if (!state) return "Нет данных";
    const raw = String(state.state ?? "");
    const normalized = raw.toLowerCase();
    if (normalized === "unavailable") return "Источник недоступен";
    if (normalized === "unknown" || !raw) return "Состояние неизвестно";
    const labels = {
      on: "Работает",
      off: "Остановлено",
      ok: "Норма",
      healthy: "Норма",
      connected: "Подключено",
      disconnected: "Нет соединения",
      running: "Работает",
      active: "Активно",
      ready: "Готово",
      standby: "Ожидание",
      warning: "Внимание",
      degraded: "Деградация",
      error: "Ошибка",
      failed: "Сбой",
      stopped: "Остановлено",
    };
    if (labels[normalized]) return labels[normalized];
    const numeric = Number(raw);
    const unit = state.attributes?.unit_of_measurement || "";
    if (Number.isFinite(numeric)) {
      const formatted = new Intl.NumberFormat(this._hass?.locale?.language || "ru", {
        maximumFractionDigits: 2,
      }).format(numeric);
      return unit ? `${formatted} ${unit}` : formatted;
    }
    return raw;
  }

  _roleInfo(role) {
    const entityId = this._roleEntityId(role);
    if (!entityId) {
      return { role, entityId: null, state: null, display: "Нет данных", tone: "unknown" };
    }
    const state = this._hass?.states?.[entityId] || null;
    if (!state) {
      return { role, entityId, state: null, display: "Источник недоступен", tone: "bad" };
    }
    return {
      role,
      entityId,
      state,
      display: this._displayState(state),
      tone: this._stateTone(state.state),
    };
  }

  _heroStatus() {
    const gateway = this._roleInfo("gateway_status");
    const tunnel = this._roleInfo("tunnel_status");
    const info = gateway.entityId ? gateway : tunnel;
    if (!info.entityId) {
      return {
        status: "Нет данных",
        detail: "API шлюза и роли сущностей ещё не подключены.",
        tone: "unknown",
        badge: "Заготовка",
      };
    }
    const sourceName = info.state?.attributes?.friendly_name || info.entityId;
    return {
      status: info.display,
      detail: `Фактическое состояние: ${sourceName}.`,
      tone: info.tone,
      badge: "Только просмотр",
    };
  }

  _renderHeader() {
    const config = this._config();
    return `<header class="nikas-shell__header">
      <button type="button" class="nikas-shell__side-action" id="menu" aria-label="Меню Home Assistant">
        <ha-icon icon="mdi:menu"></ha-icon>
      </button>
      <button type="button" class="nikas-shell__title" id="return-source" aria-label="Вернуться в исходную базовую панель NikaS">
        <strong>${escapeHtml(config.title)}</strong>
        <small>${escapeHtml(config.versionLine)}</small>
      </button>
      <button type="button" class="nikas-shell__side-action nikas-shell__side-action--right" id="refresh" aria-label="Обновить отображение">
        <ha-icon icon="mdi:refresh"></ha-icon>
      </button>
    </header>`;
  }

  _renderTabBar() {
    const tabs = this._config().tabs;
    return `<nav class="nikas-shell__tabs" style="--nikas-shell-tab-count:${Math.max(1, tabs.length)}" aria-label="Разделы">
      ${tabs.map(([view, icon, label]) => {
        const active = this._activeView === view;
        const accessible = view === "diagnostics" ? "Диагностика" : label;
        return `<button type="button" data-view="${escapeHtml(view)}" class="nikas-shell__tab${active ? " active" : ""}" aria-label="${escapeHtml(accessible)}" aria-current="${active ? "page" : "false"}">
          <ha-icon icon="${escapeHtml(icon)}"></ha-icon><small>${escapeHtml(label)}</small>
        </button>`;
      }).join("")}
    </nav>`;
  }

  _renderHero() {
    const hero = this._heroStatus();
    const tone = this._tone(hero.tone);
    return `<article class="card hero-card">
      <div class="hero-copy">
        <span class="eyebrow">ЗАЩИЩЁННЫЙ СЕТЕВОЙ ШЛЮЗ</span>
        <div class="hero-state ${tone}"><i class="status-dot ${tone}"></i><strong>${escapeHtml(hero.status)}</strong></div>
        <p>${escapeHtml(hero.detail)}</p>
      </div>
      <span class="status-badge ${tone}">${escapeHtml(hero.badge)}</span>
    </article>`;
  }

  _renderAlert(title, text, tone = "active") {
    const safeTone = this._tone(tone);
    const icon = safeTone === "bad"
      ? "mdi:alert-circle-outline"
      : safeTone === "warn"
        ? "mdi:alert-outline"
        : "mdi:information-outline";
    return `<div class="alert ${safeTone}">
      <ha-icon icon="${icon}"></ha-icon>
      <div><strong>${escapeHtml(title)}</strong><span>${escapeHtml(text)}</span></div>
    </div>`;
  }

  _renderMetric(label, role, icon = "mdi:gauge") {
    const info = this._roleInfo(role);
    const entityAttr = info.entityId
      ? ` data-entity="${escapeHtml(info.entityId)}" tabindex="0" class="metric entity-backed ${info.tone}"`
      : ` class="metric ${info.tone}"`;
    return `<article${entityAttr}>
      <div class="metric-head"><ha-icon icon="${escapeHtml(icon)}"></ha-icon><span>${escapeHtml(label)}</span></div>
      <strong>${escapeHtml(info.display)}</strong>
    </article>`;
  }

  _renderStateRow(icon, label, role) {
    const info = this._roleInfo(role);
    const entityAttr = info.entityId
      ? ` data-entity="${escapeHtml(info.entityId)}" tabindex="0"`
      : "";
    return `<div class="state-row ${info.tone}${info.entityId ? " entity-backed" : ""}"${entityAttr}>
      <ha-icon icon="${escapeHtml(icon)}"></ha-icon>
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(info.display)}</strong>
      ${info.entityId ? '<ha-icon class="chevron" icon="mdi:chevron-right"></ha-icon>' : '<span class="chevron-space"></span>'}
    </div>`;
  }

  _renderTopologyNode(role, label, icon) {
    const info = this._roleInfo(role);
    const entityAttr = info.entityId
      ? ` data-entity="${escapeHtml(info.entityId)}" tabindex="0"`
      : "";
    return `<article class="flow-node ${info.tone}${info.entityId ? " entity-backed" : ""}"${entityAttr}>
      <span class="node-icon"><ha-icon icon="${escapeHtml(icon)}"></ha-icon></span>
      <strong>${escapeHtml(label)}</strong>
      <small><i class="status-dot ${info.tone}"></i>${escapeHtml(info.display)}</small>
    </article>`;
  }

  _renderOverview() {
    return `${this._renderHero()}
      <article class="card topology-card">
        <div class="section-heading">
          <div><span class="eyebrow">ЦЕЛЕВОЙ ПОТОК</span><h2>Маршрут трафика</h2></div>
          <ha-icon icon="mdi:shield-lock-outline"></ha-icon>
        </div>
        <div class="route-flow">
          ${this._renderTopologyNode("lan_status", "Локальная сеть", "mdi:home-network-outline")}
          <ha-icon class="flow-arrow" icon="mdi:chevron-right"></ha-icon>
          ${this._renderTopologyNode("gateway_status", "VLESS Gateway", "mdi:router-network")}
          <ha-icon class="flow-arrow" icon="mdi:chevron-right"></ha-icon>
          ${this._renderTopologyNode("vless_server_status", "VLESS-сервер", "mdi:server-security")}
          <ha-icon class="flow-arrow" icon="mdi:chevron-right"></ha-icon>
          ${this._renderTopologyNode("internet_status", "Интернет", "mdi:earth")}
        </div>
      </article>
      <section class="metric-grid" aria-label="Основные параметры">
        ${this._renderMetric("Туннель", "tunnel_status", "mdi:tunnel-outline")}
        ${this._renderMetric("Активный маршрут", "active_route", "mdi:routes")}
        ${this._renderMetric("Задержка", "latency", "mdi:timer-outline")}
        ${this._renderMetric("Время работы", "uptime", "mdi:clock-check-outline")}
      </section>
      <article class="card scaffold-note">
        ${this._renderAlert(
          "Управление пока отключено",
          "Каркас остаётся read-only до утверждения API, сервисов и безопасного сценария записи.",
          "active",
        )}
      </article>`;
  }

  _renderRoutes() {
    return `<article class="card view-intro">
        <span class="eyebrow">ПОЛИТИКИ И МАРШРУТЫ</span>
        <h1>Маршрутизация</h1>
        <p>Здесь будут видны фактический режим шлюза, активный маршрут и правила обхода.</p>
      </article>
      <article class="card state-card">
        <h2>Текущее состояние</h2>
        ${this._renderStateRow("mdi:routes", "Активный маршрут", "active_route")}
        ${this._renderStateRow("mdi:tune-variant", "Режим маршрутизации", "routing_mode")}
        ${this._renderStateRow("mdi:shield-off-outline", "Правила обхода", "bypass_rules")}
        ${this._renderStateRow("mdi:clock-outline", "Последнее изменение", "last_route_change")}
      </article>
      <article class="card state-card">
        <h2>Сетевые контуры</h2>
        ${this._renderStateRow("mdi:gateway", "Маршрут по умолчанию", "default_route")}
        ${this._renderStateRow("mdi:dns-outline", "DNS-маршрут", "dns_route")}
        ${this._renderStateRow("mdi:tunnel-outline", "VLESS-туннель", "tunnel_status")}
      </article>
      <article class="card">
        ${this._renderAlert(
          "Только наблюдение",
          "Переключение маршрутов появится только после проверки атомарности, подтверждения действия и fail-closed поведения.",
          "active",
        )}
      </article>`;
  }

  _renderTraffic() {
    return `<article class="card view-intro">
        <span class="eyebrow">СЕТЕВАЯ НАГРУЗКА</span>
        <h1>Трафик</h1>
        <p>Текущая скорость, объём защищённого трафика и число соединений.</p>
      </article>
      <section class="metric-grid" aria-label="Текущий трафик">
        ${this._renderMetric("Приём", "download_rate", "mdi:download-network-outline")}
        ${this._renderMetric("Передача", "upload_rate", "mdi:upload-network-outline")}
        ${this._renderMetric("Через VLESS", "routed_traffic", "mdi:shield-check-outline")}
        ${this._renderMetric("Соединения", "active_connections", "mdi:connection")}
      </section>
      <article class="card state-card">
        <h2>Счётчики</h2>
        ${this._renderStateRow("mdi:calendar-today-outline", "За сегодня", "traffic_today")}
        ${this._renderStateRow("mdi:calendar-month-outline", "За месяц", "traffic_month")}
        ${this._renderStateRow("mdi:timer-outline", "Задержка", "latency")}
      </article>
      <article class="card">
        ${this._renderAlert(
          "История ещё не подключена",
          "Графики появятся после утверждения измеряемых сущностей и их записи в Recorder.",
          "unknown",
        )}
      </article>`;
  }

  _registryStateEntries() {
    return this._registryEntityIds.map((entityId) => ({
      entityId,
      state: this._hass?.states?.[entityId] || null,
    }));
  }

  _renderAttribute(label, value) {
    return `<div class="raw-row"><span>${escapeHtml(label)}</span><strong>${escapeHtml(diagnosticValue(value))}</strong></div>`;
  }

  _renderDiagnosticEntity(entityId, state) {
    const name = state?.attributes?.friendly_name || entityId;
    const tone = state ? this._stateTone(state.state) : "bad";
    const attributes = state?.attributes || {};
    const attributeRows = Object.entries(attributes)
      .sort(([left], [right]) => left.localeCompare(right, this._hass?.locale?.language || "ru"))
      .map(([key, value]) => this._renderAttribute(`attributes.${key}`, value))
      .join("");
    return `<article class="raw-entity entity-backed ${tone}" data-entity="${escapeHtml(entityId)}" tabindex="0">
      <div class="raw-title"><span><i class="status-dot ${tone}"></i><strong>${escapeHtml(name)}</strong></span><ha-icon icon="mdi:chevron-right"></ha-icon></div>
      ${this._renderAttribute("entity_id", entityId)}
      ${this._renderAttribute("state", state?.state ?? "Источник недоступен")}
      ${this._renderAttribute("last_changed", formatTimestamp(state?.last_changed, this._hass?.locale?.language || "ru"))}
      ${this._renderAttribute("last_updated", formatTimestamp(state?.last_updated, this._hass?.locale?.language || "ru"))}
      ${attributeRows}
    </article>`;
  }

  _renderDiagnostics() {
    const entries = this._registryStateEntries();
    let body = "";
    if (this._registryLoading && !this._registryLoaded) {
      body = this._renderLoading("Читаю реестр сущностей…");
    } else if (this._registryError && entries.length === 0) {
      body = `<article class="card">${this._renderAlert(
        "Не удалось прочитать реестр",
        this._registryError,
        "bad",
      )}</article>`;
    } else if (entries.length === 0) {
      body = `<article class="card">${this._renderAlert(
        "Сущности не найдены",
        "Интеграция пока не публикует телеметрию VLESS Gateway и роли сущностей не назначены.",
        "unknown",
      )}</article>`;
    } else {
      body = `<section class="diagnostic-grid">
        ${entries.map(({ entityId, state }) => this._renderDiagnosticEntity(entityId, state)).join("")}
      </section>`;
    }
    return `<article class="card diagnostics-intro">
        <div><span class="eyebrow">ТЕХНИЧЕСКИЙ ЭКРАН</span><h1>Диагностика</h1><p>Raw-состояния и все атрибуты сущностей VLESS Gateway.</p></div>
        <span class="status-badge active">${entries.length} сущн.</span>
      </article>
      <article class="card identity-card">
        <h2>Контракт панели</h2>
        ${this._renderAttribute("domain", VLESS_APP.domain)}
        ${this._renderAttribute("UI", this._config().versionLine)}
        ${this._renderAttribute("route", "/dashboard-vless-gateway")}
        ${this._renderAttribute("parent_route", SAFE_DEFAULT_ROUTE)}
        ${this._renderAttribute("commands", "read-only")}
      </article>
      ${body}`;
  }

  _renderLoading(message = "Загрузка панели…") {
    return `<section class="loading" aria-live="polite" aria-busy="true">
      <div class="skeleton hero-skeleton"></div>
      <div class="skeleton row-skeleton"></div>
      <div class="skeleton row-skeleton"></div>
      <span>${escapeHtml(message)}</span>
    </section>`;
  }

  _renderView(view) {
    if (this._loading) return this._renderLoading();
    const renderers = {
      overview: () => this._renderOverview(),
      routes: () => this._renderRoutes(),
      traffic: () => this._renderTraffic(),
      diagnostics: () => this._renderDiagnostics(),
    };
    return (renderers[view] || renderers.overview)();
  }

  _ensureView(view) {
    if (this._visitedViews.has(view)) return this._visitedViews.get(view);
    const slot = document.createElement("section");
    slot.className = "view-page";
    slot.dataset.viewPage = view;
    slot.hidden = true;
    slot.setAttribute("aria-hidden", "true");
    this.shadowRoot.querySelector(".nikas-shell__canvas").appendChild(slot);
    this._visitedViews.set(view, slot);
    return slot;
  }

  _activateView(view) {
    for (const [key, slot] of this._visitedViews.entries()) {
      const active = key === view;
      slot.hidden = !active;
      slot.toggleAttribute("inert", !active);
      slot.setAttribute("aria-hidden", String(!active));
    }
    this.shadowRoot.querySelectorAll(".nikas-shell__tabs button").forEach((button) => {
      const active = button.dataset.view === view;
      button.classList.toggle("active", active);
      button.setAttribute("aria-current", active ? "page" : "false");
    });
  }

  _switchView(view) {
    if (!this._validViews().has(view) || view === this._activeView) return;
    this._activeView = view;
    const slot = this._ensureView(view);
    commitStableMarkup(slot, this._renderView(view));
    this._activateView(view);
    this._attachEntityInteractions(slot);
    const controller = window.NikasPanelZoom?.attach?.(this, { min: 0.75, max: 2.0 });
    if (controller?.resetPosition) controller.resetPosition();
    else this.shadowRoot.querySelector(".nikas-shell__viewport").scrollTop = 0;
  }

  _openMoreInfo(entityId) {
    if (!validEntityId(entityId)) return;
    this.dispatchEvent(new CustomEvent("hass-more-info", {
      detail: { entityId },
      bubbles: true,
      composed: true,
    }));
  }

  _attachEntityInteractions(root = this.shadowRoot) {
    root.querySelectorAll("[data-entity]").forEach((element) => {
      if (element._vlessHoldBound) return;
      element._vlessHoldBound = true;
      let timer = null;
      let fired = false;
      const clear = () => {
        if (timer !== null) window.clearTimeout(timer);
        timer = null;
      };
      element.addEventListener("pointerdown", () => {
        fired = false;
        clear();
        timer = window.setTimeout(() => {
          fired = true;
          this._openMoreInfo(element.dataset.entity);
        }, 550);
      });
      ["pointerup", "pointercancel", "pointerleave"].forEach((name) => {
        element.addEventListener(name, clear);
      });
      element.addEventListener("click", (event) => {
        if (fired) {
          event.preventDefault();
          event.stopPropagation();
        }
      });
      element.addEventListener("keydown", (event) => {
        if (!["Enter", " "].includes(event.key)) return;
        event.preventDefault();
        this._openMoreInfo(element.dataset.entity);
      });
    });
  }

  async _loadRegistry(force = false) {
    if (!this._hass || this._registryLoading || (this._registryLoaded && !force)) return;
    this._registryLoading = true;
    this._registryError = null;
    this._queueRender();
    const roleIds = Object.values(this._entityRoles()).filter(validEntityId);
    try {
      const registry = this._hass.callWS
        ? await this._hass.callWS({ type: "config/entity_registry/list" })
        : [];
      const platformIds = Array.isArray(registry)
        ? registry
          .filter((entry) => entry?.platform === VLESS_APP.domain && validEntityId(entry.entity_id))
          .map((entry) => entry.entity_id)
        : [];
      this._registryEntityIds = [...new Set([...platformIds, ...roleIds])]
        .sort((left, right) => left.localeCompare(right, this._hass?.locale?.language || "ru"));
      this._registryLoaded = true;
    } catch (error) {
      this._registryEntityIds = [...new Set(roleIds)].sort();
      this._registryLoaded = true;
      this._registryError = error instanceof Error ? error.message : "Неизвестная ошибка";
    } finally {
      this._registryLoading = false;
      if (this._connected) this._queueRender();
    }
  }

  _queueRender() {
    if (this._renderQueued) return;
    this._renderQueued = true;
    const schedule = window.requestAnimationFrame || ((callback) => queueMicrotask(callback));
    schedule(() => {
      this._renderQueued = false;
      if (this._connected) this._render();
    });
  }

  _mountShell() {
    if (this._shellMounted) return;
    this._returnRoute = captureNikasShellReturnRoute({
      panelId: VLESS_APP.domain,
      parentRoute: this._panel?.config?.parent_route,
      safeReturnRoute: SAFE_DEFAULT_ROUTE,
    });
    this.shadowRoot.innerHTML = `<style>${nikasShellV2Styles()}${VLESS_PANEL_CSS}</style>
      <div class="nikas-shell">
        ${this._renderHeader()}
        <main class="nikas-shell__viewport canvas-viewport" aria-label="Рабочая область панели VLESS Gateway">
          <div class="nikas-shell__canvas nikas-shell__content work-canvas"></div>
        </main>
        ${this._renderTabBar()}
        <div class="scale-status" role="status" aria-live="polite">Масштаб 100%</div>
      </div>`;
    this.shadowRoot.addEventListener("click", (event) => {
      const button = event.target?.closest?.("button");
      if (!button) return;
      if (button.id === "menu") {
        this.dispatchEvent(new CustomEvent("hass-toggle-menu", { bubbles: true, composed: true }));
      } else if (button.id === "return-source") {
        navigateNikasShell(this._returnRoute);
      } else if (button.id === "refresh") {
        this._loadRegistry(true);
      } else if (button.dataset.view) {
        this._switchView(button.dataset.view);
      }
    });
    this._shellMounted = true;
    this._bindShellBoundaryGuard();
  }

  _bindShellBoundaryGuard() {
    if (!this._connected || !this._shellMounted || this._scrollGuardCleanup) return;
    const viewport = this.shadowRoot.querySelector(".nikas-shell__viewport");
    if (viewport) {
      this._scrollGuardCleanup = createNikasShellScrollBoundaryGuard({ host: this, viewport });
    }
  }

  _syncChrome() {
    const config = this._config();
    const title = this.shadowRoot.querySelector(".nikas-shell__title strong");
    const subtitle = this.shadowRoot.querySelector(".nikas-shell__title small");
    if (title.textContent !== config.title) title.textContent = config.title;
    if (subtitle.textContent !== config.versionLine) subtitle.textContent = config.versionLine;
    const refresh = this.shadowRoot.getElementById("refresh");
    refresh.classList.toggle("busy", this._registryLoading);
    refresh.setAttribute("aria-busy", String(this._registryLoading));
  }

  _render() {
    this._mountShell();
    this._syncChrome();
    const slot = this._ensureView(this._activeView);
    commitStableMarkup(slot, this._renderView(this._activeView));
    this._activateView(this._activeView);
    this._attachEntityInteractions(slot);
    window.NikasPanelZoom?.attach?.(this, { min: 0.75, max: 2.0 })?.bind?.();
  }
}

const VLESS_PANEL_CSS = `
:host{
  --vless-surface:var(--ha-card-background,var(--card-background-color,#fff));
  --vless-border:color-mix(in srgb,var(--primary-text-color,#111827) 12%,transparent);
  --vless-muted:var(--secondary-text-color,#6b7280);
  --vless-primary:var(--primary-color,#03a9f4);
  --vless-ok:#35a853;--vless-warn:#e19b00;--vless-bad:#d94b4b;--vless-unknown:#7b8794;
}
.nikas-shell__side-action#refresh.busy ha-icon{animation:vless-spin .9s linear infinite}
.view-page[hidden]{display:none!important}.view-page{display:block;min-height:100%}
.card{border:1px solid var(--vless-border);border-radius:22px;background:var(--vless-surface);padding:18px;margin-bottom:14px;box-shadow:0 2px 10px color-mix(in srgb,#000 5%,transparent)}
.card h1,.card h2,.card p{margin:0}.card h1{font-size:25px;line-height:1.15}.card h2{font-size:18px;line-height:1.25}.card p{margin-top:7px;color:var(--vless-muted);font-size:14px;line-height:1.42}
.eyebrow{display:block;margin-bottom:5px;color:var(--vless-muted);font-size:12px;font-weight:760;letter-spacing:.08em}
.hero-card{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;min-height:132px;padding:20px}.hero-copy{min-width:0}.hero-state{display:flex;align-items:center;gap:9px;font-size:25px;line-height:1.15}.hero-state strong{font-weight:820}.hero-state.ok{color:var(--vless-ok)}.hero-state.active{color:var(--vless-primary)}.hero-state.warn{color:var(--vless-warn)}.hero-state.bad{color:var(--vless-bad)}.hero-state.unknown{color:var(--vless-unknown)}
.status-dot{width:9px;height:9px;flex:0 0 9px;border-radius:50%;display:inline-block;background:var(--vless-unknown)}.status-dot.ok{background:var(--vless-ok)}.status-dot.active{background:var(--vless-primary)}.status-dot.warn{background:var(--vless-warn)}.status-dot.bad{background:var(--vless-bad)}.status-dot.unknown{background:var(--vless-unknown)}
.status-badge{flex:0 0 auto;border-radius:999px;padding:6px 9px;background:color-mix(in srgb,var(--vless-unknown) 10%,transparent);color:var(--vless-unknown);font-size:12px;font-weight:730;white-space:nowrap}.status-badge.ok{color:var(--vless-ok);background:color-mix(in srgb,var(--vless-ok) 10%,transparent)}.status-badge.active{color:var(--vless-primary);background:color-mix(in srgb,var(--vless-primary) 10%,transparent)}.status-badge.warn{color:var(--vless-warn);background:color-mix(in srgb,var(--vless-warn) 10%,transparent)}.status-badge.bad{color:var(--vless-bad);background:color-mix(in srgb,var(--vless-bad) 10%,transparent)}
.section-heading{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:14px}.section-heading>ha-icon{--mdc-icon-size:30px;color:var(--vless-primary)}
.route-flow{display:flex;flex-direction:column;align-items:stretch;gap:7px}.flow-node{min-height:82px;border:1px solid var(--vless-border);border-radius:20px;background:color-mix(in srgb,var(--vless-primary) 3%,var(--vless-surface));display:grid;grid-template-columns:42px minmax(0,1fr);grid-template-rows:auto auto;column-gap:11px;align-items:center;padding:13px 14px}.node-icon{grid-row:1/3;width:42px;height:42px;border-radius:15px;display:grid;place-items:center;background:color-mix(in srgb,var(--vless-primary) 10%,transparent);color:var(--vless-primary)}.node-icon ha-icon{--mdc-icon-size:25px}.flow-node>strong{font-size:16px}.flow-node>small{display:flex;align-items:center;gap:7px;color:var(--vless-muted);font-size:12px;font-weight:650}.flow-arrow{align-self:center;--mdc-icon-size:24px;color:var(--vless-muted);transform:rotate(90deg)}
.metric-grid{display:grid;grid-template-columns:1fr;gap:14px;margin-bottom:14px}.metric{min-width:0;min-height:86px;border:1px solid var(--vless-border);border-radius:20px;background:var(--vless-surface);padding:15px 16px;box-shadow:0 2px 10px color-mix(in srgb,#000 4%,transparent)}.metric-head{display:flex;align-items:center;gap:8px;color:var(--vless-muted);font-size:14px}.metric-head ha-icon{--mdc-icon-size:21px;color:var(--vless-primary)}.metric>strong{display:block;margin-top:8px;font-size:20px;line-height:1.2}.metric.unknown>strong{color:var(--vless-unknown)}.metric.bad>strong{color:var(--vless-bad)}.metric.warn>strong{color:var(--vless-warn)}
.view-intro{min-height:122px}.state-card h2{margin-bottom:7px}.state-row{min-height:58px;display:grid;grid-template-columns:28px minmax(0,1fr) minmax(92px,auto) 20px;gap:8px;align-items:center;padding:10px 0;border-top:1px solid var(--vless-border)}.state-row:first-of-type{border-top:0}.state-row>ha-icon:first-child{--mdc-icon-size:22px;color:var(--vless-primary)}.state-row>span{min-width:0;font-size:14px}.state-row>strong{text-align:right;font-size:14px;line-height:1.25}.state-row.unknown>strong{color:var(--vless-unknown)}.state-row.bad>strong{color:var(--vless-bad)}.state-row.warn>strong{color:var(--vless-warn)}.state-row .chevron{--mdc-icon-size:18px;color:var(--vless-muted)}
.alert{display:flex;gap:11px;align-items:flex-start;padding:14px;border:1px solid var(--vless-border);border-radius:18px;background:color-mix(in srgb,var(--vless-primary) 3%,transparent)}.alert ha-icon{--mdc-icon-size:23px;flex:0 0 23px;color:var(--vless-primary)}.alert strong,.alert span{display:block}.alert strong{font-size:14px}.alert span{margin-top:3px;color:var(--vless-muted);font-size:13px;line-height:1.4}.alert.warn ha-icon{color:var(--vless-warn)}.alert.bad ha-icon{color:var(--vless-bad)}.alert.unknown ha-icon{color:var(--vless-unknown)}
.diagnostics-intro{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}.identity-card h2{margin-bottom:8px}.diagnostic-grid{display:grid;grid-template-columns:1fr;gap:14px}.raw-entity{min-width:0;border:1px solid var(--vless-border);border-radius:22px;background:var(--vless-surface);padding:16px;box-shadow:0 2px 10px color-mix(in srgb,#000 4%,transparent)}.raw-title{display:flex;justify-content:space-between;gap:10px;align-items:center;margin-bottom:9px}.raw-title>span{min-width:0;display:flex;align-items:center;gap:8px}.raw-title strong{min-width:0;overflow-wrap:anywhere;font-size:16px}.raw-title>ha-icon{--mdc-icon-size:19px;color:var(--vless-muted)}.raw-row{display:grid;grid-template-columns:minmax(105px,.75fr) minmax(0,1.25fr);gap:10px;align-items:start;padding:8px 0;border-top:1px solid var(--vless-border);font-size:12px;line-height:1.35}.raw-row>span{min-width:0;color:var(--vless-muted);overflow-wrap:anywhere}.raw-row>strong{min-width:0;text-align:right;overflow-wrap:anywhere;font-weight:650}
.entity-backed{cursor:context-menu;-webkit-tap-highlight-color:transparent}.entity-backed:focus-visible{outline:2px solid var(--vless-primary);outline-offset:2px}
.loading{display:grid;gap:12px}.loading>span{color:var(--vless-muted);text-align:center;font-size:14px}.skeleton{border-radius:20px;background:color-mix(in srgb,var(--primary-text-color,#111827) 7%,transparent)}.hero-skeleton{min-height:140px}.row-skeleton{min-height:82px}
.scale-status{position:absolute;z-index:40;left:50%;bottom:calc(76px + env(safe-area-inset-bottom,0px));transform:translate(-50%,10px);opacity:0;pointer-events:none;padding:9px 14px;border-radius:999px;background:rgba(20,27,34,.88);color:#fff;font-size:13px;font-weight:720;white-space:nowrap;transition:opacity .14s ease,transform .14s ease}.scale-status.visible{opacity:1;transform:translate(-50%,0)}
@keyframes vless-spin{to{transform:rotate(360deg)}}
@container nikas-panel (max-width:390px){.hero-card{padding:17px}.status-badge{padding-inline:7px}.state-row{grid-template-columns:26px minmax(0,1fr) minmax(82px,auto) 18px}}
@container nikas-panel (min-width:760px){.metric-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.route-flow{flex-direction:row;align-items:stretch}.flow-node{flex:1 1 0}.flow-arrow{transform:none}.diagnostic-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@container nikas-panel (min-width:1100px){.metric-grid{grid-template-columns:repeat(4,minmax(0,1fr))}}
@media(prefers-reduced-motion:reduce){.scale-status{transition:none}.header-action.busy ha-icon{animation:none}}
`;

if (!customElements.get("vless-gateway-panel")) {
  customElements.define("vless-gateway-panel", VlessGatewayPanel);
}
