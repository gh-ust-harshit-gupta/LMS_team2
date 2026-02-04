import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api"

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
  status?: string; // "UNDER_REVIEW" | "APPROVED" | "REJECTED" | "VERIFIED"
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

type LoanItem = {
  _id: string;
  applicant_name?: string;
  status?: string;
  priority?: "normal" | "high";
  loan_type?: string; // "Home Loan" | "Personal" | etc.
  assigned_by?: string;
  assigned_at?: string;
  amount?: number;
  tenure_years?: number;
  docs?: DocItem[];
};

type Stats = { pending: number; completedToday: number; totalVerified: number };

/** ---------- Dummy Data Toggle (DEV) ---------- */
const USE_DUMMY_DATA = true;

const dummyKyc: KycItem[] = [
  {
    _id: "KYC-789456",
    applicant_name: "Rajesh Kumar",
    pan: "ABCDE1234F",
    amount: 1200000,
    tenure_months: 36,
    purpose: "Personal Loan",
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
  },
  {
    _id: "KYC-123789",
    applicant_name: "Priya Sharma",
    amount: 800000,
    tenure_months: 24,
    purpose: "Education Loan",
    applied_at: new Date(Date.now() - 26 * 60 * 60 * 1000).toISOString(),
    status: "UNDER_REVIEW",
    monthly_income: 62000,
  },
  {
    _id: "KYC-456123",
    applicant_name: "Amit Patel",
    amount: 650000,
    tenure_months: 18,
    purpose: "Vehicle Loan",
    applied_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
    status: "UNDER_REVIEW",
    monthly_income: 70000,
  },
];

const dummyLoans: LoanItem[] = [
  {
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
  },
  {
    _id: "LN-PL-2024-123",
    applicant_name: "Rohit Verma",
    loan_type: "Personal",
    amount: 500000,
    tenure_years: 3,
    assigned_by: "Manager B",
    assigned_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
    priority: "high",
    docs: [],
  },
  {
    _id: "LN-VL-2024-089",
    applicant_name: "Sneha Iyer",
    loan_type: "Vehicle",
    amount: 900000,
    tenure_years: 5,
    assigned_by: "Manager C",
    assigned_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    priority: "normal",
    docs: [],
  },
];

const dummyStats: Stats = { pending: 3, completedToday: 5, totalVerified: 128 };

/** ---------- Utils (self-contained) ---------- */
const now = () => new Date().getTime();
const ms = { hour: 3600_000, day: 24 * 3600_000 };

function priorityColorFromDate(d?: string) {
  if (!d) return { bg: "#ecfeff", fg: "#0369a1", label: "Unknown" };
  const t = new Date(d).getTime();
  const delta = now() - t;
  if (delta > ms.day) return { bg: "#fef2f2", fg: "#b91c1c", label: "Overdue" };
  if (delta > 4 * ms.hour) return { bg: "#fff7ed", fg: "#c2410c", label: "Today" };
  return { bg: "#ecfdf5", fg: "#065f46", label: "Recent" };
}

function timeAgo(d?: string) {
  if (!d) return "-";
  const t = new Date(d).getTime();
  const deltaMs = now() - t;
  if (deltaMs < ms.hour) return `${Math.max(1, Math.floor(deltaMs / 60000))}m ago`;
  if (deltaMs < ms.day) return `${Math.floor(deltaMs / ms.hour)}h ago`;
  return `${Math.floor(deltaMs / ms.day)}d ago`;
}

function formatCurrency(v?: number) {
  if (v == null) return "-";
  try {
    return v.toLocaleString("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 });
  } catch {
    return `₹${v}`;
  }
}

/** ---------- Props ---------- */
export default function DashboardPage({
  onOpenKyc,
  onOpenDoc,
}: {
  onOpenKyc?: (k: KycItem) => void;
  onOpenDoc?: (l: LoanItem) => void;
}) {
  const [kyc, setKyc] = useState<KycItem[]>([]);
  const [loans, setLoans] = useState<LoanItem[]>([]);
  const [stats, setStats] = useState<Stats>({ pending: 0, completedToday: 0, totalVerified: 0 });
  const [loading, setLoading] = useState(false);
  const [lastRefreshedAt, setLastRefreshedAt] = useState<number | null>(null);

  const navigate = useNavigate();

  const refresh = async () => {
    setLoading(true);
    try {
      if (USE_DUMMY_DATA) {
        setKyc(dummyKyc);
        setLoans(dummyLoans);
        setStats(dummyStats);
        setLastRefreshedAt(Date.now());
        return;
      }

      const [kycRes, loansRes] = await Promise.all([
        api.get("/api/verification/kyc/pending"),
        api.get("/api/verification/loans/pending-documents"),
      ]);
      setKyc(kycRes.data || []);
      setLoans(loansRes.data || []);

      try {
        const st = await api.get("/api/verification/kyc/stats");
        setStats(st.data || { pending: kycRes.data?.length ?? 0, completedToday: 0, totalVerified: 0 });
      } catch {
        setStats({ pending: kycRes.data?.length ?? 0, completedToday: 0, totalVerified: 0 });
      }
      setLastRefreshedAt(Date.now());
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  return (
    <div className="vstack gap-3" style={{ paddingBottom: 18 }}>
      {/* Header */}
      <div className="card" style={{ padding: 16, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3 style={{ margin: 0 }}>VERIFICATION DASHBOARD</h3>
        <div className="hstack" style={{ display: "flex", alignItems: "center", gap: 10 }}>
          {loading ? (
            <span style={{ fontSize: 12, color: "#667085" }}>Refreshing… ⏳</span>
          ) : lastRefreshedAt ? (
            <span style={{ fontSize: 12, color: "#667085" }}>Updated {new Date(lastRefreshedAt).toLocaleTimeString()}</span>
          ) : null}
          <button type="button" className="btn" onClick={refresh}>Refresh</button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="card" style={{ padding: 16 }}>
        <div className="hstack" style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
          <SummaryCard title="KYC Queue" value={kyc.length} icon="🧾" />
          <SummaryCard title="Doc Queue" value={loans.length} icon="📂" />
          <SummaryCard title="Pending" value={stats.pending} icon="🕑" />
          <SummaryCard title="Completed Today" value={stats.completedToday} icon="✅" />
          <SummaryCard title="Total Verified" value={stats.totalVerified} icon="📄" />
        </div>
      </div>

      {/* Pending KYC */}
      <div className="card" style={{ padding: 16 }}>
        <h4 style={{ marginBottom: 10 }}>PENDING KYC VERIFICATIONS</h4>
        <div style={{ overflowX: "auto" }}>
          <table className="table" style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <Th>Application ID</Th>
                <Th>Applicant</Th>
                <Th>Amount</Th>
                <Th>Tenure</Th>
                <Th>Purpose</Th>
                <Th>Submitted</Th>
                <Th>Priority</Th>
                <Th>Action</Th>
              </tr>
            </thead>
            <tbody>
              {kyc?.length ? (
                kyc.map((k) => {
                  const pr = priorityColorFromDate(k.applied_at);
                  return (
                    <tr key={k._id} style={{ borderTop: "1px solid #eee" }}>
                      <Td>#{k._id?.slice(-6) || "-"}</Td>
                      <Td>{k.applicant_name || k.pan || "-"}</Td>
                      <Td>{formatCurrency(k.amount)}</Td>
                      <Td>{k.tenure_months ? `${k.tenure_months}m` : "-"}</Td>
                      <Td>{k.purpose || "-"}</Td>
                      <Td>{k.applied_at ? timeAgo(k.applied_at) : "-"}</Td>
                      <Td>
                        <span style={{ background: pr.bg, color: pr.fg, padding: "4px 8px", borderRadius: 999, fontSize: 12, fontWeight: 700 }}>
                          {pr.label}
                        </span>
                      </Td>
                      <Td>
                        <button
                          type="button"
                          className="btn"
                          onClick={() => (onOpenKyc ? onOpenKyc(k) : navigate(`/verification/kyc/${k._id}`))}
                        >
                          [Verify]
                        </button>
                      </Td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <Td colSpan={8}><div style={{ textAlign: "center", padding: 20 }}>No pending KYC</div></Td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Assigned Documents */}
      <div className="card" style={{ padding: 16 }}>
        <h4 style={{ marginBottom: 10 }}>ASSIGNED DOCUMENT VERIFICATIONS</h4>
        <div style={{ overflowX: "auto" }}>
          <table className="table" style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <Th>Loan ID</Th>
                <Th>Type</Th>
                <Th>Applicant</Th>
                <Th>Assigned</Th>
                <Th>Priority</Th>
                <Th>Action</Th>
              </tr>
            </thead>
            <tbody>
              {loans?.length ? (
                loans.map((l) => {
                  const pr = priorityColorFromDate(l.assigned_at || new Date().toISOString());
                  return (
                    <tr key={l._id} style={{ borderTop: "1px solid #eee" }}>
                      <Td>#{l._id}</Td>
                      <Td>{l.loan_type || "-"}</Td>
                      <Td>{l.applicant_name || "-"}</Td>
                      <Td>{l.assigned_at ? timeAgo(l.assigned_at) : "Today"}</Td>
                      <Td>
                        <span style={{ background: pr.bg, color: pr.fg, padding: "4px 8px", borderRadius: 999, fontSize: 12, fontWeight: 700 }}>
                          {pr.label}
                        </span>
                      </Td>
                      <Td>
                        <button
                          type="button"
                          className="btn"
                          onClick={() => (onOpenDoc ? onOpenDoc(l) : navigate(`/verification/loan/${l._id}`))}
                        >
                          [Review]
                        </button>
                      </Td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <Td colSpan={6}><div style={{ textAlign: "center", padding: 20 }}>No loans waiting for document review</div></Td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

/** ---------- Small UI helpers ---------- */
function SummaryCard({ title, value, icon }: { title: string; value: number | string; icon?: string }) {
  return (
    <div className="card" style={{ padding: 12, minWidth: 220, display: "flex", gap: 6, alignItems: "center" }}>
      <div style={{ fontSize: 20 }}>{icon}</div>
      <div>
        <div style={{ fontSize: 12, color: "#667085" }}>{title}</div>
        <div style={{ fontSize: 20, fontWeight: 700 }}>{value}</div>
      </div>
    </div>
  );
}
function Th({ children }: { children: any }) {
  return <th style={{ textAlign: "left", padding: "10px 8px", color: "#667085", fontWeight: 600, fontSize: 12 }}>{children}</th>;
}
function Td({ children, colSpan }: { children: any; colSpan?: number }) {
  return <td colSpan={colSpan} style={{ padding: "10px 8px", fontSize: 14 }}>{children}</td>;
}