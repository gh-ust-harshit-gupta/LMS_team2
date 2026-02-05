import React, { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

/** ---------- Types ---------- */
type ScoreParams = {
  incomeStability: number;
  employmentType: number;
  existingEmiBurden: number;
  documentQuality: number;
};

/** ---------- Helpers ---------- */
function calculateCibilFrom100(overallOutOf100: number) {
  // Maps 0→300, 100→900 (linear)
  const s = Math.max(300, Math.min(900, Math.round(300 + (overallOutOf100 / 100) * 600)));
  return s;
}

/** ---------- Scoring Page Component ---------- */
export default function ScoringPage({
  displayLabel = "KYC Verification Scoring",
  onBack,
  onSubmit,
  immutable: immutableProp,
}: {
  displayLabel?: string;
  onBack?: () => void;
  onSubmit?: (p: ScoreParams) => void;
  immutable?: boolean;
}) {
  const navigate = useNavigate();
  const params = useParams();
  const entityType = (params.entityType || "").toLowerCase();
  const entityId = params.id;
  const labelFallback = displayLabel ?? (entityId ? `${entityType.toUpperCase()} · ${entityId}` : "UNBOUND");

  // Use prop first, fallback to false (you can later read from localStorage or context if needed)
  const [isImmutable, setIsImmutable] = useState(immutableProp ?? false);

  const [incomeStability, setIncomeStability] = useState(0);
  const [employmentType, setEmploymentType] = useState(0);
  const [existingEmiBurden, setExistingEmiBurden] = useState(0);
  const [documentQuality, setDocumentQuality] = useState(0);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Real-time total calculation
  const overall100 = incomeStability + employmentType + existingEmiBurden + documentQuality;
  const cibil = calculateCibilFrom100(overall100);

  const handleSubmit = async () => {
    if (loading || isImmutable) return;

    const payload: ScoreParams = {
      incomeStability,
      employmentType,
      existingEmiBurden,
      documentQuality,
    };

    if (onSubmit) {
      onSubmit(payload);
      setIsImmutable(true); // mark as done even in callback mode
      return;
    }

    // Validate context
    if (!entityId || !entityType) {
      setError("Invalid context — cannot save score.");
      return;
    }
    if (entityType === "loan") {
      setError("Loan-level scoring must be submitted from the Document Verification page or via an onSubmit handler.");
      return;
    }
    if (entityType !== "kyc") {
      setError("Unsupported entity type for scoring.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const api = (await import("../api")).default;

      await api.post(`/api/verification/kyc/${entityId}/score`, null, {
        params: {
          income_score: payload.incomeStability,
          emi_burden_score: payload.existingEmiBurden,
          employment_score: payload.employmentType,
          experience_score: payload.documentQuality,
        },
      });

      // Mark as submitted (prevents re-submit)
      setIsImmutable(true);

      // Optional: store that it was submitted (helps when reopening page)
      localStorage.setItem(`kyc_scored_${entityId}`, "true");

      // Go back to KYC detail
      navigate(`/verification/kyc/${entityId}`);
    } catch (err: any) {
      console.error("Score save failed:", err);
      const msg =
        err?.response?.data?.message ||
        err?.message ||
        "Failed to save scores. Please check your connection and try again.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  // Optional: if reopening the page, check if already submitted
  React.useEffect(() => {
    if (entityId && localStorage.getItem(`kyc_scored_${entityId}`) === "true") {
      setIsImmutable(true);
    }
  }, [entityId]);

  return (
    <div className="card" style={{ padding: 24, maxWidth: 600, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h3 style={{ margin: 0 }}>VERIFICATION SCORING — {labelFallback}</h3>
        <button type="button" className="btn" onClick={() => (onBack ? onBack() : navigate(-1))}>
          Back
        </button>
      </div>

      <p style={{ color: "#667085", marginBottom: 20 }}>
        Assign manual scores (0–25) for each parameter. Total is used for credit decisioning. Once submitted, scores are immutable.
      </p>

      <div style={{ fontWeight: 600, marginBottom: 12 }}>SCORING PARAMETERS (0–25 each)</div>

      <ScoreField
        label="Income Stability"
        value={incomeStability}
        onChange={setIncomeStability}
        disabled={isImmutable}
        description="Unstable / irregular (0) → Very stable & predictable (25)"
      />

      <ScoreField
        label="Employment Type"
        value={employmentType}
        onChange={setEmploymentType}
        disabled={isImmutable}
        description="Unemployed / temporary (0) → Permanent / Govt / PSU (25)"
      />

      <ScoreField
        label="Existing EMI Burden"
        value={existingEmiBurden}
        onChange={setExistingEmiBurden}
        disabled={isImmutable}
        description="High burden / over-leveraged (0) → Low / no EMI (25)"
      />

      <ScoreField
        label="Document Quality & Experience"
        value={documentQuality}
        onChange={setDocumentQuality}
        disabled={isImmutable}
        description="Poor / missing / inconsistent (0) → Excellent / complete (25)"
      />

      <div style={{ marginTop: 24, padding: 16, background: "#f8fafc", borderRadius: 8 }}>
        <div style={{ fontSize: 18, fontWeight: 700 }}>
          Overall Score:{" "}
          <span
            style={{
              color: overall100 >= 70 ? "#16a34a" : overall100 >= 40 ? "#d97706" : "#e63946",
            }}
          >
            {overall100} / 100
          </span>
        </div>
        <div style={{ fontSize: 16, marginTop: 8 }}>
          Equivalent CIBIL: <strong>{cibil}</strong>
        </div>
      </div>

      {error && (
        <div style={{ color: "#e63946", marginTop: 16, padding: 12, background: "#fef2f2", borderRadius: 6 }}>
          {error}
        </div>
      )}

      <button
        type="button"
        className="btn"
        style={{
          width: "100%",
          marginTop: 24,
          padding: 12,
          fontSize: 16,
          background: isImmutable ? "#94a3b8" : loading ? "#6b7280" : "#16a34a",
          color: "#fff",
          cursor: isImmutable || loading ? "not-allowed" : "pointer",
        }}
        disabled={isImmutable || loading}
        onClick={handleSubmit}
      >
        {isImmutable
          ? "Scores Already Submitted (Immutable)"
          : loading
          ? "Saving Scores..."
          : "Submit Scores"}
      </button>
    </div>
  );
}

/** ---------- Reusable Score Field ---------- */
function ScoreField({
  label,
  value,
  onChange,
  disabled,
  description,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  disabled?: boolean;
  description: string;
}) {
  return (
    <div style={{ marginBottom: 20 }}>
      <div style={{ fontWeight: 600, marginBottom: 6 }}>{label}</div>
      <div style={{ fontSize: 13, color: "#667085", marginBottom: 8 }}>{description}</div>
      <input
        type="number"
        min={0}
        max={25}
        step={1}
        value={value}
        onChange={(e) => {
          let v = parseInt(e.target.value, 10);
          if (isNaN(v)) v = 0;
          v = Math.max(0, Math.min(25, v));
          onChange(v);
        }}
        disabled={disabled}
        style={{
          width: 90,
          padding: 8,
          fontSize: 16,
          border: "1px solid #d1d5db",
          borderRadius: 6,
        }}
      />
      <span style={{ marginLeft: 12, fontWeight: 500 }}>{value} / 25</span>
    </div>
  );
}