
// import PersonalLoanInfo from "./pages/persinfo";
// import HomeLoanInfo from "./pages/homeinfo";
// import VehicleLoanInfo from "./pages/vehinfo";
// import EducationLoanInfo from "./pages/eduinfo";

// function App() {
//   return (
//     <div>
//       <PersonalLoanInfo />
//       <HomeLoanInfo />
//       <VehicleLoanInfo />
//       <EducationLoanInfo />
//     </div>
//   );
// }

// export default App;


// import CustomerLogin from "./pages/CustomerLogin";

// function App() {
//   return <CustomerLogin />;
// }

// export default App;

import EmiRepayment from "./components/EmiRepayment";
import "./styles/loan-application.css";

function App() {
  return (
    <EmiRepayment
      title="EMI Repayment"
      loanSummary={{
        loanId: "LMS-2024-00123",
        customerName: "Personal Loan",
        amount: "Rs 650,000",
        interestRate: "12.5% p.a.",
        tenure: "36 months",
      }}
      emiStatus={{
        monthlyEmi: "Rs 15,972",
        nextDueDate: "05 Jun 2024",
        status: "Current",
        paidOn: "02 Jun 2024",
        totalPaid: "Rs 91,844",
        balance: "Rs 4,58,156",
        overdue: "0",
        remarks: "All good",
      }}
      quickActions={[
        { label: "Pay EMI" },
        { label: "Auto Pay" },
        { label: "Statement" },
      ]}
      upcomingPayments={[
        {
          no: 1,
          dueDate: "05 Jul 2024",
          principal: "14,630",
          interest: "1,342",
          total: "15,972",
        },
        {
          no: 2,
          dueDate: "05 Aug 2024",
          principal: "14,854",
          interest: "1,118",
          total: "15,972",
        },
      ]}
      paymentHistory={[
        {
          no: 1,
          dueDate: "05 May 2024",
          paidDate: "05 May 2024",
          amount: "15,972",
          status: "Paid",
        },
        {
          no: 2,
          dueDate: "05 Apr 2024",
          paidDate: "05 Apr 2024",
          amount: "15,972",
          status: "Paid",
        },
      ]}
      upcomingFooterNote="Showing 2 of 34 remaining payments."
      historyFooterNote="Showing last 2 payments."
    />
  );
}
 
export default App;
