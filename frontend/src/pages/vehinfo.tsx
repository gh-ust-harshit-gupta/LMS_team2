import LoanInfoLayout from "../components/LoanInfoLayout";
import { vehicleLoan } from "../components/loanContent";

export default function VehicleLoanInfo() {
  return (
    <LoanInfoLayout
      title={vehicleLoan.title}
      content={vehicleLoan}
    />
  );
}
