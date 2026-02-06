import LoanInfoLayout from "../components/LoanInfoLayout";
import { homeLoan } from "../components/loanContent";

export default function HomeLoanInfo() {
  return (
    <LoanInfoLayout
      title={homeLoan.title}
      content={homeLoan}
    />
  );
}
