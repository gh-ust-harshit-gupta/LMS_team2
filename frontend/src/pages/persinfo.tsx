import LoanInfoLayout from "../components/LoanInfoLayout";
import { personalLoan } from "../data/loanContent";

export default function PersonalLoanInfo() {
  return <LoanInfoLayout title={personalLoan.title} content={personalLoan} />;
}
