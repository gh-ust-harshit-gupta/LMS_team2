import { useState } from "react";

interface Props {
  loan: {
    amount: number;
    tenure: number;
    purpose: string;
  };
  documents: string[];
  emi: number;
  onBack: () => void;
  onSubmit: () => void;
}

export default function ReviewSubmit({
  loan,
  documents,
  emi,
  onBack,
  onSubmit,
}: Props) {
  const [confirmInfo, setConfirmInfo] = useState(false);
  const [agreeTerms, setAgreeTerms] = useState(false);
  const [authorizeCheck, setAuthorizeCheck] = useState(false);

  const isSubmitEnabled = confirmInfo && agreeTerms && authorizeCheck;

  // Defensive guard (bank-grade safety)
  if (!loan) return null;

  return (
    <div className="review-wrapper">
      {/* LOAN SUMMARY */}
      <div className="review-card">
        <h3 className="card-title">Loan Summary</h3>

        <div className="summary-row">
          <span>Loan Amount</span>
          <strong>₹{loan.amount.toLocaleString()}</strong>
        </div>

        <div className="summary-row">
          <span>Tenure</span>
          <strong>{loan.tenure} months</strong>
        </div>

        <div className="summary-row">
          <span>Purpose</span>
          <strong>{loan.purpose}</strong>
        </div>

        <div className="summary-row highlight">
          <span>Estimated EMI</span>
          <strong>₹{emi} / month</strong>
        </div>
      </div>

      {/* DOCUMENTS */}
      <div className="review-card">
        <h3 className="card-title">Documents Uploaded</h3>

        {documents.length === 0 ? (
          <p className="muted-text">No documents uploaded</p>
        ) : (
          <ul className="doc-list">
            {documents.map((doc) => (
              <li key={doc}>✔ {doc}</li>
            ))}
          </ul>
        )}
      </div>

      {/* DECLARATIONS */}
      <div className="review-card">
        <h3 className="card-title">Declarations</h3>

        <label className="declaration-row">
          <input
            type="checkbox"
            checked={confirmInfo}
            onChange={(e) => setConfirmInfo(e.target.checked)}
          />
          <span>I confirm the information provided is correct</span>
        </label>

        <label className="declaration-row">
          <input
            type="checkbox"
            checked={agreeTerms}
            onChange={(e) => setAgreeTerms(e.target.checked)}
          />
          <span>I agree to the Terms & Conditions</span>
        </label>

        <label className="declaration-row">
          <input
            type="checkbox"
            checked={authorizeCheck}
            onChange={(e) => setAuthorizeCheck(e.target.checked)}
          />
          <span>I authorize credit and document verification</span>
        </label>
      </div>

      {/* ACTION BAR */}
      <div className="action-bar">
        <button className="btn-outline" onClick={onBack}>
          ← Back
        </button>

        <button
          className={`btn-primary ${!isSubmitEnabled ? "disabled" : ""}`}
          disabled={!isSubmitEnabled}
          onClick={onSubmit}
        >
          Submit Application
        </button>
      </div>
    </div>
  );
}
