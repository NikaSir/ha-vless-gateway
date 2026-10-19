import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
let Panel;
const context = vm.createContext({HTMLElement: class {}, customElements: {get: () => undefined, define: (_name, value) => { Panel = value; }}, Intl});
vm.runInContext(fs.readFileSync("custom_components/vless_gateway/frontend/src/vless-gateway-panel.js", "utf8"), context);
const panel = Object.create(Panel.prototype);
panel._panel = {config: {entity_roles: {routed_traffic: "sensor.actual_total"}}};
panel._hass = {states: {"sensor.actual_total": {state: "150", attributes: {unit_of_measurement: "B"}}}};
const html = panel._renderTraffic();
assert.ok(html.includes("Трафик sing-box"), "DIRECT-inclusive total must describe its measured scope");
assert.ok(html.includes("DIRECT") && html.includes("VLESS") && html.toLowerCase().includes("обход"), "scope must distinguish kernel bypass");
assert.ok(!html.includes("Через VLESS") && !html.includes("защищённого"));
for (const [state, tone, label] of [["degraded_fail_open", "warn", "DIRECT: резервный режим"], ["control_error", "bad", "Ошибка управления"], ["starting", "warn", "Запуск"]]) {
 assert.equal(panel._stateTone(state), tone);
 assert.equal(panel._displayState({state}), label);
}
console.log("Factual traffic scope and gateway failure states passed");
