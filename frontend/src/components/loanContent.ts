export type LoanSection = {
  title: string;
  features: string[];
  eligibility: string[];
  howToAvail: string[];
};

export const personalLoan: LoanSection = {
  title: "Personal Loan",
  features: [
    "Unsecured loan without collateral",
    "Eligibility decided by internal credit decision engine",
    "Fixed EMI with flexible tenure options",
    "Fully digital loan application and approval flow",
    "Transparent and explainable credit decisioning",
  ],
  eligibility: [
    "Employees from Government, Defence, PSU, or Corporate sector",
    "Approved KYC is mandatory",
    "Minimum internal credit score required",
    "Existing EMIs must be within allowed limits",
    "Applicant must be an Indian resident",
  ],
  howToAvail: [
    "Register and complete KYC on LMS platform",
    "Check eligible loan amount on dashboard",
    "Apply for Personal Loan and submit documents",
    "Track approval and disbursement digitally",
  ],
};

export const homeLoan: LoanSection = {
  title: "Home Loan",
  features: [
    "Secured loan for residential property purchase",
    "Long tenure with structured EMI repayment",
    "Lower interest rate based on eligibility score",
    "Property verification and valuation workflow",
    "Multi-level approval process",
  ],
  eligibility: [
    "Approved KYC and verified income",
    "Valid property documents required",
    "Stable employment or business income",
    "Internal credit score eligibility",
    "EMI affordability check mandatory",
  ],
  howToAvail: [
    "Complete KYC and profile verification",
    "Select Home Loan from dashboard",
    "Submit property and loan details",
    "Upload documents and track approval",
  ],
};

export const vehicleLoan: LoanSection = {
  title: "Vehicle Loan",
  features: [
    "Loan for two-wheeler or four-wheeler purchase",
    "Quick digital approval process",
    "Moderate tenure with fixed EMI",
    "Vehicle-based eligibility evaluation",
    "Online tracking through LMS dashboard",
  ],
  eligibility: [
    "Approved KYC required",
    "Stable income source mandatory",
    "Vehicle quotation or invoice required",
    "Existing EMI limits apply",
    "Internal credit score evaluation",
  ],
  howToAvail: [
    "Complete KYC verification",
    "Select Vehicle Loan option",
    "Enter vehicle and loan details",
    "Submit documents for approval",
  ],
};

export const educationLoan: LoanSection = {
  title: "Education Loan",
  features: [
    "Financial support for higher education",
    "Deferred repayment during course period",
    "Covers tuition and academic expenses",
    "Guarantor-based eligibility assessment",
    "Structured approval workflow",
  ],
  eligibility: [
    "Confirmed admission from recognized institution",
    "Guarantor details mandatory",
    "KYC completed for applicant and guarantor",
    "Internal credit assessment required",
    "EMI affordability evaluated",
  ],
  howToAvail: [
    "Complete KYC process",
    "Submit education and institution details",
    "Upload admission and fee documents",
    "Track loan decision digitally",
  ],
};
