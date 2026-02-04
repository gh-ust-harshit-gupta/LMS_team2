import LoanInfoLayout from "../components/LoanInfoLayout";
import { homeLoan } from "../data/loanContent";

export default function HomeLoanInfo() {
  return (
    <LoanInfoLayout
      title={homeLoan.title}
      content={homeLoan}
    />
  );
}
