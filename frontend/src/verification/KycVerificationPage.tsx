import React, { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";

/** ---------- Types (self-contained) ---------- */
type AnyMap = Record<string, any>;
type DocStatus = "pending" | "verified" | "rejected";
type DocItem = { name: string; url?: string; pages?: number; status?: DocStatus; category?: "PROPERTY" | "FINANCIAL" };

type KycItem = {
  _id: string;
  pan?: string;
  applicant_name?: string;
  amount?: number;
  tenure_months?: number;
  purpose?: string;
  applied_at?: string;
  status?: string;
  monthly_income?: number;
  cibil_score?: number;
  docs?: DocItem[];
  dob?: string;
  gender?: string;
  nationality?: string;
  address_current?: string;
  address_permanent?: string;
  employer?: string;
  designation?: string;
  employment_type?: string;
  experience_years?: number;
};

/** ---------- Helpers ---------- */
function calculateCibilFrom100(overallOutOf100: number) {
  const s = Math.max(300, Math.min(900, Math.round(300 + (overallOutOf100 / 100) * 600)));
  return s;
}
function timeAgo(d?: string) {
  if (!d) return "-";
  const t = new Date(d).getTime();
  const delta = Date.now() - t;
  const hour = 3600_000, day = 24 * hour;
  if (delta < hour) return `${Math.max(1, Math.floor(delta / 60000))}m ago`;
  if (delta < day) return `${Math.floor(delta / hour)}h ago`;
  return `${Math.floor(delta / day)}d ago`;
}
function formatCurrency(v?: number) {
  if (v == null) return "-";
  try { return v.toLocaleString("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }); } catch { return `₹${v}`; }
}

/** ---------- Demo fallback when no props ---------- */
const USE_DEMO_IF_NO_PROP = true;
const DEMO_KYC: KycItem = {
  _id: "KYC-789456",
  applicant_name: "Rajesh Kumar",
  pan: "ABCDE1234F",
  applied_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
  status: "UNDER_REVIEW",
  monthly_income: 85000,
  dob: "1985-08-15",
  gender: "Male",
  nationality: "Indian",
  employer: "Tech Solutions Inc.",
  designation: "Senior Manager",
  employment_type: "Permanent",
  experience_years: 8,
  address_current: "H-201, Green Valley, Mumbai - 400072",
  address_permanent: "Same as current",
  docs: [
    { name: "PAN Card", status: "pending" },
    { name: "Aadhaar Card", status: "pending" },
    { name: "Salary Slip - March 2024", status: "pending" },
    { name: "Form 16 - AY 2023-24", status: "pending" },
    { name: "Utility Bill (Address Proof)", status: "pending" },
  ],
};

/** ---------- Component ---------- */
export default function KycVerificationPage({
  item: itemProp,
  onBack,
  onRequireScoring,
  scores,
}: {
  item?: KycItem;
  onBack?: () => void;
  onRequireScoring?: () => void;
  scores?: { submitted: boolean; overall100: number; cibil: number };
}) {
  const item = itemProp || (USE_DEMO_IF_NO_PROP ? DEMO_KYC : undefined);
  const navigate = useNavigate();
  if (!item) return <div className="card" style={{ padding: 16 }}>No KYC selected.</div>;

  const [checks, setChecks] = useState({
    idConsistency: false,
    ageNationality: false,
    employmentCredibility: false,
    addressCorrectness: false,
  });

  const [docState, setDocState] = useState<Record<string, DocStatus>>(() =>
    (item.docs || DEMO_KYC.docs!).reduce((acc, d) => ((acc[d.name] = d.status || "pending"), acc), {} as Record<string, DocStatus>)
  );

  const [notes, setNotes] = useState("");
  const [rejectOpen, setRejectOpen] = useState(false);
  const [rejectReason, setRejectReason] = useState("");
  const [rejectNotes, setRejectNotes] = useState("");

  const allChecked = Object.values(checks).every(Boolean);
  const allDocsVerified = Object.values(docState).every((s) => s === "verified");

  // 0–25 buckets (kept for backend compatibility)
  const breakdown = useMemo(() => {
    const incomeScore = checks.employmentCredibility ? 25 : 0;
    const obligationScore = checks.idConsistency ? 25 : 0;
    const employmentScore = checks.employmentCredibility ? 25 : 0;
    const experienceScore = checks.addressCorrectness ? 25 : 0;
    const overall100 = incomeScore + obligationScore + employmentScore + experienceScore;
    const cibil = calculateCibilFrom100(overall100);
    return { incomeScore, obligationScore, employmentScore, experienceScore, overall100, cibil };
  }, [checks]);

  const scoringReady = !!scores?.submitted;
  const approveDisabled = !(allChecked && allDocsVerified && (scoringReady || true /* allow local breakdown if no scoring */));

  const handleApprove = async () => {
    await api.post(`/api/verification/kyc/${item._id}/verify`, null, {
      params: {
        income_score: breakdown.incomeScore,
        emi_burden_score: breakdown.obligationScore,
        employment_score: breakdown.employmentScore,
        experience_score: breakdown.experienceScore,
        overall_score: scores?.overall100 ?? breakdown.overall100,
        cibil_score: scores?.cibil ?? breakdown.cibil,
        decision: "approved",
        notes: notes || undefined,
      },
    });
    onBack?.();
  };

  const handleRejectConfirm = async () => {
    if (!rejectReason) return;
    await api.post(`/api/verification/kyc/${item._id}/verify`, null, {
      params: {
        income_score: 0,
        emi_burden_score: 0,
        employment_score: 0,
        experience_score: 0,
        overall_score: 0,
        cibil_score: 300,
        decision: "rejected",
        notes: `${rejectReason}${rejectNotes ? ` — ${rejectNotes}` : ""}`,
      },
    });
    setRejectOpen(false);
    onBack?.();
  };

  return (
    <div className="vstack gap-3" style={{ paddingBottom: 18 }}>
      <div className="card" style={{ padding: 16, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3 style={{ margin: 0 }}>
          KYC VERIFICATION - {item._id} <span style={{ fontSize: 12, color: "#667085", marginLeft: 8 }}>({item.applicant_name || item.pan || "-"})</span>
        </h3>
        <button type="button" className="btn" onClick={() => (onBack ? onBack() : navigate(-1))}>Back to Queue</button>
      </div>

      {/* Customer Header */}
      <div className="card" style={{ padding: 16, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <div style={{ fontWeight: 700 }}>CUSTOMER: {item.applicant_name || item.pan || "-"}</div>
          <div style={{ fontSize: 12, color: "#667085" }}>SUBMITTED: {timeAgo(item.applied_at)}</div>
        </div>
        <StatusPill status={item.status || "UNDER_REVIEW"} />
      </div>

      {/* Personal & Identity */}
      <div className="card" style={{ padding: 16 }}>
        <div className="hstack" style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 16 }}>
          {/* Personal */}
          <div className="card" style={{ padding: 12 }}>
            <div style={{ fontWeight: 700, marginBottom: 8 }}>
              PERSONAL INFORMATION <span style={{ fontSize: 12, color: "#667085", marginLeft: 8 }}>[Edit Toggle: ▢]</span>
            </div>
            <div className="grid" style={{ display: "grid", gridTemplateColumns: "repeat(2,1fr)", gap: 8 }}>
              <Info label="Name" value={item.applicant_name || "-"} />
              <Info label="DOB" value={item.dob || "-"} />
              <Info label="Gender" value={item.gender || "-"} />
              <Info label="Nationality" value={item.nationality || "Indian"} />
            </div>
          </div>

          {/* Identity */}
          <div className="card" style={{ padding: 12 }}>
            <div style={{ fontWeight: 700, marginBottom: 8 }}>IDENTITY DOCUMENTS</div>
            <div className="hstack" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
              {["PAN Card", "Aadhaar Card"].map((nm) => (
                <DocTile
                  key={nm}
                  name={nm}
                  status={docState[nm] || "pending"}
                  onView={() => window.open("#", "_blank")}
                  onVerify={() => setDocState((s) => ({ ...s, [nm]: "verified" }))}
                />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Employment & Income */}
      <div className="card" style={{ padding: 16 }}>
        <div style={{ fontWeight: 700, marginBottom: 8 }}>EMPLOYMENT & INCOME DETAILS</div>
        <div className="grid" style={{ display: "grid", gridTemplateColumns: "repeat(2,1fr)", gap: 12 }}>
          <Info label="Company" value={item.employer || "Tech Solutions Inc."} />
          <Info label="Designation" value={item.designation || "Senior Manager"} />
          <Info label="Monthly Income" value={formatCurrency(item.monthly_income || 85000)} />
          <Info label="Employment Type" value={item.employment_type || "Permanent"} />
          <Info label="Experience" value={`${item.experience_years ?? 8} years`} />
        </div>
        <div className="card" style={{ padding: 12, marginTop: 12 }}>
          <div style={{ fontWeight: 700, marginBottom: 8 }}>[Uploaded Documents]</div>
          {["Salary Slip - March 2024", "Form 16 - AY 2023-24"].map((nm) => (
            <DocLine
              key={nm}
              name={nm}
              status={docState[nm] || "pending"}
              onView={() => window.open("#", "_blank")}
              onVerify={() => setDocState((s) => ({ ...s, [nm]: "verified" }))}
            />
          ))}
        </div>
      </div>

      {/* Address */}
      <div className="card" style={{ padding: 16 }}>
        <div style={{ fontWeight: 700, marginBottom: 8 }}>ADDRESS DETAILS</div>
        <div className="grid" style={{ display: "grid", gridTemplateColumns: "repeat(2,1fr)", gap: 12 }}>
          <Info label="Current" value={item.address_current || "H-201, Green Valley, Mumbai - 400072"} />
          <Info label="Permanent" value={item.address_permanent || "Same as current"} />
        </div>
        <div style={{ marginTop: 10 }}>
          <DocLine
            name="Utility Bill (Address Proof)"
            status={docState["Utility Bill (Address Proof)"] || "pending"}
            onView={() => window.open("#", "_blank")}
            onVerify={() => setDocState((s) => ({ ...s, ["Utility Bill (Address Proof)"]: "verified" }))}
          />
        </div>
      </div>

      {/* Actions */}
      <div className="card" style={{ padding: 16 }}>
        <div style={{ fontWeight: 700, marginBottom: 8 }}>VERIFICATION ACTIONS</div>
        <ChecklistItem label="Cross-check identity consistency" checked={checks.idConsistency} onChange={(v) => setChecks((c) => ({ ...c, idConsistency: v }))} />
        <ChecklistItem label="Validate age and nationality eligibility" checked={checks.ageNationality} onChange={(v) => setChecks((c) => ({ ...c, ageNationality: v }))} />
        <ChecklistItem label="Verify employment and income credibility" checked={checks.employmentCredibility} onChange={(v) => setChecks((c) => ({ ...c, employmentCredibility: v }))} />
        <ChecklistItem label="Confirm address correctness" checked={checks.addressCorrectness} onChange={(v) => setChecks((c) => ({ ...c, addressCorrectness: v }))} />

        <div className="card" style={{ padding: 12, marginTop: 12 }}>
          <div style={{ fontWeight: 600, marginBottom: 6 }}>Notes</div>
          <textarea rows={3} style={{ width: "100%" }} placeholder="Add notes…" value={notes} onChange={(e) => setNotes(e.target.value)} />
        </div>

        <div className="hstack" style={{ display: "flex", gap: 8, justifyContent: "space-between", marginTop: 12 }}>
          <button type="button" className="btn" style={{ background: "#e53935", color: "#fff" }} onClick={() => setRejectOpen(true)}>REJECT KYC</button>
          <div style={{ display: "flex", gap: 8 }}>
            {!scores?.submitted && (
              <button
                type="button"
                className="btn"
                onClick={() => (onRequireScoring ? onRequireScoring() : navigate(`/verification/score/kyc/${item._id}`))}
              >
                Open Scoring
              </button>
            )}
            <button
              type="button"
              className="btn"
              style={{ background: approveDisabled ? "#94a3b8" : "#16a34a", color: "#fff" }}
              disabled={approveDisabled}
              onClick={handleApprove}
            >
              APPROVE KYC
            </button>
          </div>
        </div>
      </div>

      {/* Reject Modal */}
      {rejectOpen && (
        <Modal title="Reject KYC" onClose={() => setRejectOpen(false)}>
          <div className="vstack" style={{ display: "flex", gap: 10 }}>
            <div>
              <div style={{ fontSize: 12, color: "#667085", marginBottom: 4 }}>Rejection Reason (Required)</div>
              <select style={{ width: "100%", padding: 8 }} value={rejectReason} onChange={(e) => setRejectReason(e.target.value)}>
                <option value="">▽ Select reason…</option>
                <option value="Identity mismatch">Identity mismatch</option>
                <option value="Fraudulent/forged document">Fraudulent/forged document</option>
                <option value="Employment not verifiable">Employment not verifiable</option>
                <option value="Address not valid">Address not valid</option>
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
                onClick={handleRejectConfirm}
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

/** ---------- UI Helpers ---------- */
function StatusPill({ status }: { status: string }) {
  const map: AnyMap = {
    UNDER_REVIEW: { bg: "#fff7ed", fg: "#c2410c", text: "UNDER REVIEW" },
    VERIFIED: { bg: "#ecfeff", fg: "#0369a1", text: "VERIFIED" },
    APPROVED: { bg: "#ecfdf5", fg: "#065f46", text: "APPROVED" },
    REJECTED: { bg: "#fef2f2", fg: "#b91c1c", text: "REJECTED" },
  };
  const s = map[status] || map["UNDER_REVIEW"];
  return <span style={{ background: s.bg, color: s.fg, padding: "4px 8px", borderRadius: 999, fontSize: 12, fontWeight: 700 }}>{s.text}</span>;
}
function Info({ label, value }: { label: string; value: any }) {
  return (
    <div className="card" style={{ padding: 10 }}>
      <div style={{ fontSize: 12, color: "#667085" }}>{label}</div>
      <div style={{ fontWeight: 600 }}>{value}</div>
    </div>
  );
}
function DocTile({ name, status, onView, onVerify }: { name: string; status: DocStatus; onView: () => void; onVerify: () => void }) {
  return (
    <div className="card" style={{ padding: 10 }}>
      <div style={{ fontWeight: 600, marginBottom: 8 }}>{name}</div>
      <div style={{ height: 60, background: "#f3f4f6", borderRadius: 6, marginBottom: 8 }} />
      <div className="hstack" style={{ display: "flex", gap: 8 }}>
        <button type="button" className="btn" onClick={onView}>View</button>
        <button type="button" className="btn" onClick={onVerify} disabled={status === "verified"}>{status === "verified" ? "Verified ✓" : "Verify"}</button>
      </div>
    </div>
  );
}
function DocLine({ name, status, onView, onVerify }: { name: string; status: DocStatus; onView: () => void; onVerify: () => void }) {
  return (
    <div className="hstack" style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderTop: "1px solid #eee", alignItems: "center" }}>
      <span>█ {name}</span>
      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
        <span style={{ fontSize: 12, color: "#667085" }}>{status === "verified" ? "Verified ✓" : status === "rejected" ? "Rejected" : "Pending"}</span>
        <button type="button" className="btn" onClick={onView}>View</button>
        <button type="button" className="btn" onClick={onVerify} disabled={status === "verified"}>{status === "verified" ? "Verified" : "Verify"}</button>
      </div>
    </div>
  );
}
function ChecklistItem({ label, checked, onChange }: { label: string; checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <div className="hstack" style={{ display: "flex", gap: 8, alignItems: "center", padding: "6px 0" }}>
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} /> <span>{label}</span>
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