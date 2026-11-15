import test from "node:test";
import assert from "node:assert/strict";
import { createEmailDeliveryReportReader, reportReason, type EmailDeliveryHistory } from "./deliveryReports.ts";
import { contactHash } from "./contactIdentity.ts";

const provider = "00000000-0000-4000-8000-000000000001";
const employee = "00000000-0000-4000-8000-000000000002";
const resource = "/subscriptions/00000000-0000-4000-8000-000000000003/resourceGroups/example/providers/Microsoft.Communication/communicationServices/example";
const workspace = "00000000-0000-4000-8000-000000000004";
const env = { EMAIL_DELIVERY_REPORTS_RESOURCE_ID: resource, EMAIL_DELIVERY_REPORTS_WORKSPACE_ID: workspace };
const now = Date.parse("2026-10-28T15:00:00Z");
const history: EmailDeliveryHistory = { deliveryId: employee, channel: "email", recipientRole: "caregiver", status: "accepted", createdAtUtc: "2026-10-27T14:00:00Z", providerId: provider, contactHash: contactHash("email", "person@example.invalid"), recipientEmployeeId: employee, recipientName: "Example Person" };
const columns = ["CorrelationId", "RecipientId", "DeliveryStatus", "TimeGenerated", "SmtpStatusCode", "EnhancedSmtpStatusCode"].map(name => ({ name }));
const bounce = [provider.toUpperCase(), "PERSON@example.invalid", "Bounced", "2026-10-27T14:07:00Z", "550", "5.1.1"];
function fixture(rows: unknown[][] = [bounce]) {
  let time = now;
  const requests: { url: string; init?: RequestInit }[] = [];
  const read = createEmailDeliveryReportReader({ now: () => time, token: async () => "test-token", fetch: async (url, init) => {
    requests.push({ url: String(url), init }); return new Response(JSON.stringify({ tables: [{ columns, rows }] }));
  } });
  return { read, requests, advance: () => { time += 61000; } };
}

test("a late bounce overlays acceptance and binds both exact provider and recipient hash", async () => {
  const f = fixture(); const result = await f.read([history], true, env);
  assert.equal(result.deliveries[0].status, "accepted"); // Never reopen the sending claim.
  assert.equal(result.deliveries[0].deliveryReport?.reason, "address_not_found");
  assert.equal(result.deliveries[0].recipientAddress, "person@example.invalid");
  assert.equal(result.deliveries[0].reviewContactHref, `/employees/${employee}`);
  assert.equal("providerId" in result.deliveries[0], false);
  assert.equal("contactHash" in result.deliveries[0], false);
  assert.equal("recipientEmployeeId" in result.deliveries[0], false);
  assert.equal(f.requests.length, 1);
  assert.equal(f.requests[0].url, `https://api.loganalytics.azure.com/v1/workspaces/${workspace}/query`);
  const body = JSON.parse(String(f.requests[0].init?.body));
  assert.equal(body.timespan, "P30D");
  assert.ok(body.query.includes(provider));
  assert.ok(!body.query.includes("person@example.invalid"));
  assert.ok(!body.query.includes("FailureMessage"));
});

test("other recipients, provider IDs, pre-send and future events cannot attach to this delivery", async () => {
  for (const row of [
    [provider, "other@example.invalid", ...bounce.slice(2)],
    [employee, ...bounce.slice(1)],
    [provider, bounce[1], bounce[2], "2026-10-26T14:07:00Z", ...bounce.slice(4)],
    [provider, bounce[1], bounce[2], "2026-10-29T14:07:00Z", ...bounce.slice(4)],
    [provider, null, ...bounce.slice(2)],
  ]) {
    const result = await fixture([row]).read([history], true, env);
    assert.equal(result.deliveries[0].deliveryReport, null);
    assert.equal(result.deliveries[0].recipientAddress, null);
  }
});

test("Supervisor projections mask the address and expose no Admin navigation or internal correlation", async () => {
  const result = await fixture().read([history], false, env);
  assert.equal(result.deliveries[0].recipientAddress, "p***@example.invalid");
  assert.equal(result.deliveries[0].reviewContactHref, null);
  assert.equal(JSON.stringify(result).includes("person@example.invalid"), false);
});

test("resource/id allowlists and the fifty-row bound prevent arbitrary queries", async () => {
  const f = fixture();
  await f.read([history], true, { ...env, EMAIL_DELIVERY_REPORTS_RESOURCE_ID: resource + "/../other?query=all" });
  await f.read([{ ...history, providerId: 'injected"); union *' }], true, env);
  await f.read([{ ...history, channel: "sms" }], true, env);
  await assert.rejects(f.read(Array(51).fill(history), true, env));
  assert.equal(f.requests.length, 0);
});

test("missing configuration and absent reports do not claim delivery", async () => {
  const f = fixture([]);
  assert.equal((await f.read([history], true, {})).deliveryReports.status, "not_configured");
  const result = await f.read([history], true, env);
  assert.equal(result.deliveryReports.status, "available");
  assert.equal(result.deliveries[0].deliveryReport, null);
  assert.equal(result.deliveries[0].status, "accepted");
});

test("failed and partial log reads preserve history without leaking raw errors or confirming delivery", async () => {
  for (const response of [new Response('private provider error', { status: 403 }), new Response(JSON.stringify({ error: { code: 'PartialError', message: 'private payload' }, tables: [{ columns, rows: [bounce] }] })), new Response('{not json')]) {
    const read = createEmailDeliveryReportReader({ now: () => now, token: async () => "test", fetch: async () => response });
    const result = await read([history], true, env);
    assert.equal(result.deliveryReports.status, "unavailable");
    assert.equal(result.deliveries.length, 1);
    assert.equal(result.deliveries[0].deliveryReport, null);
    assert.equal(JSON.stringify(result).includes("private"), false);
  }
});

test("queries are cached for sixty seconds and still project each actor's access independently", async () => {
  const f = fixture();
  await Promise.all([f.read([history], true, env), f.read([history], false, env)]);
  assert.equal(f.requests.length, 1);
  f.advance(); await f.read([history], true, env);
  assert.equal(f.requests.length, 2);
});

test("Delivered is a transport result, while SMTP and filtering reasons remain distinct", async () => {
  const delivered = await fixture([[...bounce.slice(0, 2), "Delivered", ...bounce.slice(3)]]).read([history], true, env);
  assert.equal(delivered.deliveries[0].deliveryReport?.state, "Delivered");
  assert.equal(delivered.deliveries[0].deliveryReport?.reason, "delivered");
  assert.equal(reportReason("Bounced", "552", "5.2.2"), "mailbox_full");
  assert.equal(reportReason("FilteredSpam", null, null), "spam_filtered");
  assert.equal(reportReason("Quarantined", null, null), "quarantined");
});


test("workspace configuration is required and cannot redirect queries or share cached evidence", async () => {
  const f = fixture();
  for (const bad of [undefined, "", "other/../../query", "https://example.invalid", workspace + "?query=all"]) {
    const result = await f.read([history], true, { ...env, EMAIL_DELIVERY_REPORTS_WORKSPACE_ID: bad });
    assert.equal(result.deliveryReports.status, "not_configured");
  }
  assert.equal(f.requests.length, 0);
  await f.read([history], true, env);
  await f.read([history], true, { ...env, EMAIL_DELIVERY_REPORTS_WORKSPACE_ID: employee });
  assert.equal(f.requests.length, 2);
  for (const request of f.requests) {
    assert.ok(JSON.parse(String(request.init?.body)).query.includes(JSON.stringify(resource)));
  }
});
