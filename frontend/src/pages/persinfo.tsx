import LoanInfoLayout from "../components/LoanInfoLayout";
import { personalLoan } from "../components/loanContent";

export default function PersonalLoanInfo() {
  return <LoanInfoLayout title={personalLoan.title} content={personalLoan} />;
}
