import { contactAddress, contactHash } from "./contactIdentity.ts";

export type EmailDeliveryHistory = {
  deliveryId: string; channel: string; recipientRole: string; status: string;
  createdAtUtc: string | Date; attemptedAtUtc?: string | Date | null;
  completedAtUtc?: string | Date | null; providerId?: string | null;
  contactHash?: string | null; recipientEmployeeId?: string; recipientName?: string;
};
type Report = { providerId: string; address: string; state: string; at: string; reason: string };
type QueryResult = { status: "available" | "unavailable" | "not_configured"; checkedAtUtc: string | null; reports: Report[] };
type Dependencies = {
  fetch: typeof fetch; now: () => number;
  token: (signal: AbortSignal) => Promise<string>;
};
const providerPattern = /^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/i;
const resourcePattern = /^\/subscriptions\/[a-f0-9-]{36}\/resourceGroups\/[a-z0-9_.()-]+\/providers\/Microsoft\.Communication\/communicationServices\/[a-z0-9-]+$/i;
const terminalStates = new Set(["Delivered", "Bounced", "Failed", "Suppressed", "FilteredSpam", "Quarantined"]);
const retainedDays = 30;

export function reportReason(state: string, smtp: unknown, enhanced: unknown) {
  if (state === "Delivered") return "delivered";
  if (state === "FilteredSpam") return "spam_filtered";
  if (state === "Quarantined") return "quarantined";
  if (state === "Suppressed") return "suppressed";
  if (/^[245]\.1\.1$/.test(String(enhanced))) return "address_not_found";
  if (/^[245]\.2\.2$/.test(String(enhanced))) return "mailbox_full";
  if (/^5/.test(String(smtp))) return "recipient_rejected";
  return "delivery_failed";
}

/** Fixed-resource, bounded read only. Never change a send ledger or retry a message. */
export function createEmailDeliveryReportReader(overrides: Partial<Dependencies> = {}) {
  const deps: Dependencies = {
    fetch: (...args) => fetch(...args), now: Date.now,
    token: async () => { throw Error("Inject an authorized token adapter; local reference has no Azure login"); }, ...overrides,
  };
  const cache = new Map<string, { until: number; result: Promise<QueryResult> }>();
  async function query(resource: string, workspace: string, ids: string[]): Promise<QueryResult> {
    try {
      const signal = AbortSignal.timeout(8000);
      const token = await deps.token(signal);
      const query = `ACSEmailStatusUpdateOperational
| where _ResourceId =~ ${JSON.stringify(resource)}
| where CorrelationId in~ (${ids.map(id => JSON.stringify(id)).join(",")})
| where isnotempty(RecipientId)
| where DeliveryStatus in ("Delivered","Bounced","Failed","Suppressed","FilteredSpam","Quarantined")
| summarize arg_max(TimeGenerated,DeliveryStatus,SmtpStatusCode,EnhancedSmtpStatusCode) by CorrelationId,RecipientId
| project CorrelationId,RecipientId,DeliveryStatus,TimeGenerated,SmtpStatusCode,EnhancedSmtpStatusCode
| take 101`;
      const response = await deps.fetch(`https://api.loganalytics.azure.com/v1/workspaces/${workspace}/query`, {
        method: "POST", redirect: "error", signal,
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ query, timespan: `P${retainedDays}D` }),
      });
      if (!response.ok) throw Error("Delivery reports unavailable");
      const text = await response.text();
      if (text.length > 256000) throw Error("Delivery reports too large");
      const body = JSON.parse(text);
      if (body.error || !Array.isArray(body.tables) || body.tables.length !== 1) throw Error("Incomplete delivery reports");
      const table = body.tables[0];
      const expected = ["CorrelationId", "RecipientId", "DeliveryStatus", "TimeGenerated", "SmtpStatusCode", "EnhancedSmtpStatusCode"];
      if (!Array.isArray(table.columns) || table.columns.length !== expected.length ||
        table.columns.some((c: { name?: string }, i: number) => c?.name !== expected[i]) ||
        !Array.isArray(table.rows) || table.rows.length > 100) throw Error("Invalid delivery report contract");
      const reports: Report[] = [];
      for (const row of table.rows) {
        if (!Array.isArray(row) || row.length !== expected.length) throw Error("Invalid delivery row");
        const [id, recipient, state, at, smtp, enhanced] = row;
        if (typeof id !== "string" || !ids.includes(id.toLowerCase()) || !terminalStates.has(state) ||
          typeof at !== "string" || !Number.isFinite(Date.parse(at)) || Date.parse(at) > deps.now() + 60000 ||
          Date.parse(at) < deps.now() - retainedDays * 86400000) continue;
        let address: string;
        try { address = contactAddress("email", recipient); } catch { continue; }
        reports.push({ providerId: id.toLowerCase(), address, state, at: new Date(at).toISOString(), reason: reportReason(state, smtp, enhanced) });
      }
      return { status: "available", checkedAtUtc: new Date(deps.now()).toISOString(), reports };
    } catch {
      // No raw provider errors, query parameters, addresses or tokens reach logs/UI.
      return { status: "unavailable", checkedAtUtc: null, reports: [] };
    }
  }
  return async function read(rows: EmailDeliveryHistory[], revealRecipient: boolean, env: NodeJS.ProcessEnv = process.env) {
    if (rows.length > 50) throw Error("Delivery history exceeds its bound");
    const resource = env.EMAIL_DELIVERY_REPORTS_RESOURCE_ID ?? "";
    const workspace = env.EMAIL_DELIVERY_REPORTS_WORKSPACE_ID ?? "";
    const configured = resourcePattern.test(resource) && providerPattern.test(workspace);
    const ids = [...new Set(rows.filter(r => r.channel === "email" && providerPattern.test(r.providerId ?? ""))
      .map(r => r.providerId!.toLowerCase()))].sort();
    let result: QueryResult = { status: "not_configured", checkedAtUtc: null, reports: [] };
    if (configured && ids.length) {
      const key = `${workspace.toLowerCase()}:${resource.toLowerCase()}:${ids.join(",")}`;
      let entry = cache.get(key);
      if (!entry || entry.until <= deps.now()) {
        if (cache.size >= 128) cache.delete(cache.keys().next().value!);
        entry = { until: deps.now() + 60000, result: query(resource, workspace, ids) };
        cache.set(key, entry);
      }
      result = await entry.result;
    } else if (configured) result = { status: "available", checkedAtUtc: null, reports: [] };
    const deliveries = rows.map(row => {
      const { providerId, contactHash: hash, recipientEmployeeId, ...visible } = row;
      const matches = result.reports.filter(r => r.providerId === providerId?.toLowerCase() &&
        typeof hash === "string" && contactHash("email", r.address) === hash.toLowerCase() &&
        Date.parse(r.at) >= Date.parse(String(row.createdAtUtc)) - 60000);
      matches.sort((a, b) => Date.parse(b.at) - Date.parse(a.at));
      const report = row.channel === "email" ? matches[0] : undefined;
      const recipientAddress = report ? (revealRecipient ? report.address : `${report.address[0]}***@${report.address.split("@")[1]}`) : null;
      return { ...visible, recipientAddress,
        reviewContactHref: revealRecipient && providerPattern.test(recipientEmployeeId ?? "") ? `/employees/${recipientEmployeeId}` : null,
        deliveryReport: report ? { state: report.state, reason: report.reason, reportedAtUtc: report.at } : null,
      };
    });
    return { deliveries, deliveryReports: { status: result.status, checkedAtUtc: result.checkedAtUtc, retentionDays: retainedDays, cacheSeconds: 60 } };
  };
}
export const readEmailDeliveryReports = createEmailDeliveryReportReader();
