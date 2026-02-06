import LoanInfoLayout from "../components/LoanInfoLayout";
import { educationLoan } from "../components/loanContent";

export default function EducationLoanInfo() {
  return (
    <LoanInfoLayout
      title={educationLoan.title}
      content={educationLoan}
    />
  );
}
