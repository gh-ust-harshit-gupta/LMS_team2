import { useState } from "react";
import ProgressStep from "../components/ProgressStep";
import ApplicantDetails from "../components/ApplicantDetails";
import { DocumentUpload } from "../components/DocumentUpload";
import ReviewSubmit from "../components/ReviewSubmit";
import Confirmation from "../components/Confirmation";
import TrackStatus, { TimelineItem } from "../components/TrackStatus";

import "../styles/loan-application.css";

type LoanType = "personal" | "home" | "vehicle" | "education";

interface Props {
  loanType: LoanType;
}

/** Loan configuration */
const LOAN_CONFIG: Record<LoanType, { interest: number; purposes: string[] }> = {
  personal: {
    interest: 12.5,
    purposes: ["Medical Expenses", "Wedding", "Travel", "Personal Use"],
  },
  home: {
    interest: 8.75,
    purposes: ["Home Purchase", "Construction", "Renovation"],
  },
  vehicle: {
    interest: 9.5,
    purposes: ["Two Wheeler Purchase", "Four Wheeler Purchase"],
  },
  education: {
    interest: 7.9,
    purposes: ["Tuition Fees", "Overseas Education", "Exam Fees"],
  },
};

const LoanApplication = ({ loanType }: Props) => {
  const [step, setStep] = useState<number>(1);
  const [showTrackStatus, setShowTrackStatus] = useState(false);
  const timelineItems: TimelineItem[] = [
    {
      title: "Application Submitted",
      time: "May 14, 2024 · 10:30 AM",
      status: "completed",
      note: "Application received successfully.",
    },
    {
      title: "Document Verification",
      time: "May 16, 2024 · 2:15 PM",
      status: "in-progress",
      note: "Your documents are being verified.",
    },
    {
      title: "Risk Assessment",
      status: "pending",
      note: "Credit assessment will begin after document verification.",
    },
    {
      title: "Manager Review",
      status: "pending",
      note: "Final approval by lending manager.",
    },
    {
      title: "Sanction Approved",
      status: "pending",
      note: "Sanction letter will be generated.",
    },
    {
      title: "Sanction Letter Sent",
      status: "completed",
      note: "You will receive the sanction letter via email.",
    },
    {
      title: "Amount Disbursed",
      status: "pending",
      note: "Funds will be transferred to your account.",
    },
  ];

  /* Applicant Details */
  const [applicant, setApplicant] = useState({
    fullName: "",
    age: 0,
    employmentType: "",
    monthlyIncome: 0,
    existingEmi: 0,
  });

  /* Loan Details */
  const [loanData, setLoanData] = useState({
    amount: 500000,
    tenure: 36,
    purpose: LOAN_CONFIG[loanType].purposes[0],
  });

  const [documents, setDocuments] = useState<string[]>([]);

  /** EMI Calculation (mock - backend will replace) */
  const monthlyRate = LOAN_CONFIG[loanType].interest / 12 / 100;
  const emi = Math.round(
    (loanData.amount *
      monthlyRate *
      Math.pow(1 + monthlyRate, loanData.tenure)) /
      (Math.pow(1 + monthlyRate, loanData.tenure) - 1)
  );

  /* Simple eligibility check (frontend mock) */
  const isEligible =
    applicant.monthlyIncome > 0 &&
    applicant.monthlyIncome * 0.5 > applicant.existingEmi + emi;

  const next = () => setStep((s) => Math.min(s + 1, 5));
  const back = () => setStep((s) => Math.max(s - 1, 1));

  return (
    <div className="loan-wrapper">
      <div className="loan-container">
        {/* HEADER */}
        <div className="loan-header">
          <h1>Apply for {loanType.toUpperCase()} Loan</h1>
          <p>Complete the steps below to submit your loan application</p>
        </div>

        {/* PROGRESS BAR */}
        <ProgressStep step={step} />

        {/* STEP 1 - APPLICANT DETAILS */}
        {step === 1 && (
          <ApplicantDetails applicant={applicant} onChange={setApplicant} />
        )}

        {/* STEP 2 - LOAN DETAILS */}
        {step === 2 && (
          <div className="step-card">
            <h3>Loan Details</h3>

            <div className="form-group">
              <label>Loan Amount</label>
              <input
                type="number"
                min={50000}
                value={loanData.amount}
                onChange={(e) =>
                  setLoanData({ ...loanData, amount: +e.target.value })
                }
              />
            </div>

            <div className="form-group">
              <label>Loan Tenure</label>
              <select
                value={loanData.tenure}
                onChange={(e) =>
                  setLoanData({ ...loanData, tenure: +e.target.value })
                }
              >
                {[12, 24, 36, 48, 60].map((m) => (
                  <option key={m} value={m}>
                    {m} Months
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Purpose</label>
              <select
                value={loanData.purpose}
                onChange={(e) =>
                  setLoanData({ ...loanData, purpose: e.target.value })
                }
              >
                {LOAN_CONFIG[loanType].purposes.map((p) => (
                  <option key={p}>{p}</option>
                ))}
              </select>
            </div>

            <div className="emi-card">
              <div className="emi-row">
                <span>Interest Rate</span>
                <strong>{LOAN_CONFIG[loanType].interest}% p.a.</strong>
              </div>
              <div className="emi-row highlight">
                <span>Estimated EMI</span>
                <strong>Rs {emi} / month</strong>
              </div>
            </div>

            {!isEligible && (
              <p className="error-text">
                Based on your income and existing EMI, you are currently not
                eligible.
              </p>
            )}
          </div>
        )}

        {/* STEP 3 - DOCUMENTS */}
        {step === 3 && (
          <DocumentUpload loanType={loanType} onUpload={setDocuments} />
        )}

        {/* STEP 4 - REVIEW */}
        {step === 4 && (
          <ReviewSubmit
            loan={loanData}
            documents={documents}
            emi={emi}
            onBack={back}
            onSubmit={next}
          />
        )}

        {/* STEP 5 - CONFIRMATION / TRACK STATUS */}
        {step === 5 && !showTrackStatus && (
          <Confirmation onTrackStatus={() => setShowTrackStatus(true)} />
        )}
        {step === 5 && showTrackStatus && (
          <TrackStatus
            items={timelineItems}
            sanctionLetter={{
              isAvailable: true,
              fileName: "sanction-letter.txt",
              issuedOn: "May 18, 2024",
              referenceId: "SAN-2024-0012",
              fileContent:
                "Sanction Letter\n\nYour loan has been approved subject to standard terms and conditions.\n\nRegards,\nLMS Bank",
              fileMimeType: "text/plain",
            }}
            onBack={() => setShowTrackStatus(false)}
            backLabel="Back to Confirmation"
          />
        )}

        {/* ACTION BUTTONS */}
        {step < 4 && (
          <div className="button-row">
            {step > 1 && (
              <button className="btn-outline" onClick={back}>
                Back
              </button>
            )}
            <button className="btn-primary" onClick={next}>
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default LoanApplication;
