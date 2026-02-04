import React, { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";

/** ---------- Types ---------- */
type DocStatus = "pending" | "verified" | "rejected";
type DocItem = { name: string; url?: string; pages?: number; status?: DocStatus; category?: "PROPERTY" | "FINANCIAL" };
type LoanItem = {
  _id: string;
  applicant_name?: string;
  status?: string;
  priority?: "normal" | "high";
  loan_type?: string;
  assigned_by?: string;
  assigned_at?: string;
  amount?: number;
  tenure_years?: number;
  docs?: DocItem[];
};

/** ---------- Helpers ---------- */
function groupDocs(docs: DocItem[]): { PROPERTY: DocItem[]; FINANCIAL: DocItem[] } {
  return { PROPERTY: docs.filter((d) => (d.category || "PROPERTY") === "PROPERTY"), FINANCIAL: docs.filter((d) => d.category === "FINANCIAL") };
}
function updateDoc(
  setDocs: React.Dispatch<React.SetStateAction<{ PROPERTY: DocItem[]; FINANCIAL: DocItem[] }>>,
  bucket: "PROPERTY" | "FINANCIAL",
  idx: number,
  patch: Partial<DocItem>
) {
  setDocs((prev) => {
    const next = { ...prev, [bucket]: [...prev[bucket]] };
    next[bucket][idx] = { ...next[bucket][idx], ...patch };
    return next;
  });
}
function progressPct(list: DocItem[]) {
  const n = list.length;
  if (!n) return 0;
  const approved = list.filter((d) => d.status === "verified").length;
  return Math.round((approved / n) * 100);
}
function flattenDocsForPost(d: { PROPERTY: DocItem[]; FINANCIAL: DocItem[] }) {
  return [...d.PROPERTY, ...d.FINANCIAL].map((x) => ({ doc_name: x.name, status: x.status || "pending" }));
}
function formatCurrency(v?: number) {
  if (v == null) return "-";
  try { return v.toLocaleString("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }); } catch { return `₹${v}`; }
}

/** ---------- Demo fallback ---------- */
const USE_DEMO_IF_NO_PROP = true;
const DEMO_LOAN: LoanItem = {
  _id: "LN-HL-2024-056",
  applicant_name: "Anjali Mehta",
  loan_type: "Home Loan",
  amount: 2500000,
  tenure_years: 15,
  assigned_by: "Manager A",
  assigned_at: new Date().toISOString(),
  priority: "normal",
  docs: [
    { name: "Sale Agreement", pages: 15, status: "pending", category: "PROPERTY" },
    { name: "Property Tax Receipt", pages: 2, status: "pending", category: "PROPERTY" },
    { name: "NOC from Society", pages: 3, status: "pending", category: "PROPERTY" },
    { name: "Bank Statements - Last 6 months", pages: 6, status: "pending", category: "FINANCIAL" },
    { name: "Salary Slips - Last 3 months", pages: 3, status: "pending", category: "FINANCIAL" },
  ],
};

/** ---------- Component ---------- */
export default function DocumentVerificationPage({
  loan: loanProp,
  onBack,
  onRequireScoring,
  scores,
}: {
  loan?: LoanItem;
  onBack?: () => void;
  onRequireScoring?: () => void;
  scores?: { submitted: boolean; overall100: number; cibil: number };
}) {
  const loan = loanProp || (USE_DEMO_IF_NO_PROP ? DEMO_LOAN : undefined);
  const navigate = useNavigate();
  if (!loan) return <div className="card" style={{ padding: 16 }}>No Loan selected.</div>;

  const [docs, setDocs] = useState<{ PROPERTY: DocItem[]; FINANCIAL: DocItem[] }>(() => groupDocs(loan.docs || DEMO_LOAN.docs!));
  const propertyProgress = useMemo(() => progressPct(docs.PROPERTY), [docs.PROPERTY]);
  const financialProgress = useMemo(() => progressPct(docs.FINANCIAL), [docs.FINANCIAL]);
  const allVerified = propertyProgress === 100 && financialProgress === 100;

  const [rejectOpen, setRejectOpen] = useState(false);
  const [rejectReason, setRejectReason] = useState("");
  const [rejectNotes, setRejectNotes] = useState("");

  const doApprove = async () => {
    const payload = flattenDocsForPost(docs);
    await api.post(`/api/verification/loans/${loan._id}/documents/verify`, payload);
    onBack?.();
  };

  const doReject = async () => {
    if (!rejectReason) return;
    const payload = flattenDocsForPost(docs).map((d) => ({ ...d, status: "rejected" as const }));
    await api.post(`/api/verification/loans/${loan._id}/documents/verify`, payload);
    setRejectOpen(false);
    onBack?.();
  };

  return (
    <div className="vstack gap-3" style={{ paddingBottom: 18 }}>
      <div className="card" style={{ padding: 16, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3 style={{ margin: 0 }}>DOCUMENT VERIFICATION - {loan._id}</h3>
        <button type="button" className="btn" onClick={() => (onBack ? onBack() : navigate(-1))}>Back to Queue</button>
      </div>

      <div className="card" style={{ padding: 16, display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 12 }}>
        <Info label="Loan" value={`${loan.loan_type || "Loan"} | ${formatCurrency(loan.amount || 2500000)} | ${loan.tenure_years || 15} Years`} />
        <Info label="Customer" value={loan.applicant_name || "-"} />
        <Info label="Assigned By" value={loan.assigned_by || "Manager A"} />
        <Info label="Priority" value={<Badge label="Normal" />} />
      </div>

      <div className="card" style={{ padding: 16 }}>
        <div style={{ fontWeight: 700, marginBottom: 8 }}>REQUIRED DOCUMENTS ({loan.loan_type || "Loan"})</div>

        <div className="card" style={{ padding: 12, marginBottom: 10 }}>
          <div style={{ fontWeight: 700, marginBottom: 6 }}>PROPERTY DOCUMENTS</div>
          {docs.PROPERTY.map((d, idx) => (
            <DocRow
              key={idx}
              doc={d}
              onView={() => window.open(d.url || "#", "_blank")}
              onVerify={() => updateDoc(setDocs, "PROPERTY", idx, { status: "verified" })}
              onReject={() => updateDoc(setDocs, "PROPERTY", idx, { status: "rejected" })}
            />
          ))}
        </div>

        <div className="card" style={{ padding: 12 }}>
          <div style={{ fontWeight: 700, marginBottom: 6 }}>FINANCIAL DOCUMENTS</div>
          {docs.FINANCIAL.map((d, idx) => (
            <DocRow
              key={idx}
              doc={d}
              onView={() => window.open(d.url || "#", "_blank")}
              onVerify={() => updateDoc(setDocs, "FINANCIAL", idx, { status: "verified" })}
              onReject={() => updateDoc(setDocs, "FINANCIAL", idx, { status: "rejected" })}
            />
          ))}
        </div>
      </div>

      <div className="card" style={{ padding: 16 }}>
        <div style={{ fontWeight: 700, marginBottom: 8 }}>DOCUMENT VERIFICATION CHECKLIST</div>
        <Checkline label="Check document authenticity" />
        <Checkline label="Confirm completeness and clarity" />
        <Checkline label="Validate document-to-loan consistency" />

        <div className="grid" style={{ display: "grid", gridTemplateColumns: "repeat(2,1fr)", gap: 12, marginTop: 12 }}>
          <div className="card" style={{ padding: 12 }}>
            <div style={{ fontWeight: 600, marginBottom: 6 }}>Property Docs</div>
            <ProgressBar pct={propertyProgress} />
          </div>
          <div className="card" style={{ padding: 12 }}>
            <div style={{ fontWeight: 600, marginBottom: 6 }}>Financial Docs</div>
            <ProgressBar pct={financialProgress} />
          </div>
        </div>
      </div>

      <div className="card" style={{ padding: 16 }}>
        <div className="hstack" style={{ display: "flex", gap: 8, justifyContent: "space-between" }}>
          <button type="button" className="btn" style={{ background: "#16a34a", color: "#fff" }} disabled={!allVerified} onClick={doApprove}>DOCUMENTS VERIFIED</button>
          <div style={{ display: "flex", gap: 8 }}>
            {!scores?.submitted && (
              <button
                type="button"
                className="btn"
                onClick={() => (onRequireScoring ? onRequireScoring() : navigate(`/verification/score/loan/${loan._id}`))}
              >
                Open Scoring
              </button>
            )}
            <button type="button" className="btn" style={{ background: "#e53935", color: "#fff" }} onClick={() => setRejectOpen(true)}>REJECT DOCUMENTS</button>
          </div>
        </div>
      </div>

      {rejectOpen && (
        <Modal title="Reject Documents" onClose={() => setRejectOpen(false)}>
          <div className="vstack" style={{ display: "flex", gap: 10 }}>
            <div>
              <div style={{ fontSize: 12, color: "#667085", marginBottom: 4 }}>Rejection Reason (Required)</div>
              <select style={{ width: "100%", padding: 8 }} value={rejectReason} onChange={(e) => setRejectReason(e.target.value)}>
                <option value="">▽ Select reason…</option>
                <option value="Incomplete document set">Incomplete document set</option>
                <option value="Low quality/not readable">Low quality/not readable</option>
                <option value="Mismatch with loan details">Mismatch with loan details</option>
                <option value="Suspected forgery">Suspected forgery</option>
              </select>
            </div>
            <div>
              <div style={{ fontSize: 12, color: "#667085", marginBottom: 4 }}>Additional Comments (Optional)</div>
              <textarea rows={3} style={{ width: "100%" }} value={rejectNotes} onChange={(e) => setRejectNotes(e.target.value)} />
            </div>
            <div className="hstack" style={{ display: "flex", justifyContent: "flex-end", gap: 8 }}>
              <button type="button" className="btn" onClick={() => setRejectOpen(false)}>Cancel</button>
              <button
                type="button"
                className="btn"
                style={{ background: rejectReason ? "#e53935" : "#94a3b8", color: "#fff" }}
                disabled={!rejectReason}
                onClick={doReject}
              >
                Confirm Reject
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}

/** ---------- UI helpers ---------- */
function Info({ label, value }: { label: string; value: any }) {
  return (
    <div className="card" style={{ padding: 10 }}>
      <div style={{ fontSize: 12, color: "#667085" }}>{label}</div>
      <div style={{ fontWeight: 600 }}>{value}</div>
    </div>
  );
}
function Badge({ label }: { label: string }) {
  return <span style={{ background: "#eef2ff", color: "#3730a3", padding: "2px 8px", borderRadius: 999, fontSize: 12, fontWeight: 700 }}>{label}</span>;
}
function DocRow({ doc, onView, onVerify, onReject }: { doc: DocItem; onView: () => void; onVerify: () => void; onReject: () => void }) {
  return (
    <div className="card" style={{ padding: 10, marginBottom: 8 }}>
      <div className="hstack" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <div style={{ fontWeight: 600 }}>█ {doc.name} {doc.pages ? `- ${doc.pages} pages` : ""}</div>
          <div style={{ fontSize: 12, color: "#667085" }}>Status: {doc.status || "pending"}</div>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button type="button" className="btn" onClick={onView}>View</button>
          <button type="button" className="btn" onClick={onVerify} disabled={doc.status === "verified"}>Mark Verified</button>
          <button type="button" className="btn" onClick={onReject} disabled={doc.status === "rejected"}>Reject</button>
        </div>
      </div>
    </div>
  );
}
function Checkline({ label }: { label: string }) {
  const [v, setV] = useState(false);
  return (
    <div className="hstack" style={{ display: "flex", gap: 8, alignItems: "center", padding: "6px 0" }}>
      <input type="checkbox" checked={v} onChange={(e) => setV(e.target.checked)} /> <span>{label}</span>
    </div>
  );
}
function ProgressBar({ pct }: { pct: number }) {
  return (
    <div>
      <div style={{ background: "#e5e7eb", height: 10, borderRadius: 999, overflow: "hidden" }}>
        <div style={{ width: `${pct}%`, height: 10, background: "#0ea5e9" }} />
      </div>
      <div style={{ fontSize: 12, color: "#667085", marginTop: 6 }}>{pct}% Complete</div>
    </div>
  );
}
function Modal({ title, onClose, children }: { title: string; onClose: () => void; children: any }) {
  return (
    <div
      role="dialog"
      aria-modal="true"
      className="modal-backdrop"
      style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.25)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 40 }}
      onClick={onClose}
    >
      <div className="card" style={{ width: 680, maxWidth: "95vw", background: "#fff", padding: 18, borderRadius: 10 }} onClick={(e) => e.stopPropagation()}>
        <div className="hstack" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
          <h4 style={{ margin: 0 }}>{title}</h4>
          <button type="button" className="btn" onClick={onClose}>✕</button>
        </div>
        {children}
      </div>
    </div>
  );
}