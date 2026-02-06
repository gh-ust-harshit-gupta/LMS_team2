interface ConfirmationProps {
  onTrackStatus: () => void;
}

export default function Confirmation({ onTrackStatus }: ConfirmationProps) {
  return (
    <div className="confirmation-card">
      <div className="confirmation-icon">Success</div>
      <h2>Application Submitted</h2>
      <p>
        Your loan application has been successfully submitted. Our verification team
        will review your documents.
      </p>

      <div className="review-card" style={{ marginTop: 20 }}>
        <h4>Next Steps</h4>
        <p>Verification by internal team</p>
        <p>Credit decision</p>
        <p>Status updates on dashboard</p>
      </div>

      <div className="button-row" style={{ marginTop: 24 }}>
        <button className="btn-primary" onClick={onTrackStatus}>
          Track Status
        </button>
      </div>
    </div>
  );
}
