import LoanInfoLayout from "../components/LoanInfoLayout";
import { vehicleLoan } from "../data/loanContent";

export default function VehicleLoanInfo() {
  return (
    <LoanInfoLayout
      title={vehicleLoan.title}
      content={vehicleLoan}
    />
  );
}
