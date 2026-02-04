import LoanInfoLayout from "../components/LoanInfoLayout";
import { educationLoan } from "../data/loanContent";

export default function EducationLoanInfo() {
  return (
    <LoanInfoLayout
      title={educationLoan.title}
      content={educationLoan}
    />
  );
}
