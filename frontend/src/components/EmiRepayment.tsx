interface LoanSummary {
  loanId: string;
  customerName: string;
  amount: string;
  interestRate: string;
  tenure: string;
}

interface EmiStatus {
  monthlyEmi: string;
  nextDueDate: string;
  status: string;
  paidOn: string;
  totalPaid: string;
  balance: string;
  overdue: string;
  remarks: string;
}

interface QuickAction {
  label: string;
  onClick?: () => void;
}

interface ScheduleRow {
  no: number;
  dueDate: string;
  principal: string;
  interest: string;
  total: string;
}

interface PaymentRow {
  no: number;
  dueDate: string;
  paidDate: string;
  amount: string;
  status: string;
}

interface EmiRepaymentProps {
  title?: string;
  loanSummary: LoanSummary;
  emiStatus: EmiStatus;
  quickActions: QuickAction[];
  upcomingPayments: ScheduleRow[];
  paymentHistory: PaymentRow[];
  upcomingFooterNote?: string;
  historyFooterNote?: string;
}

export default function EmiRepayment({
  title = "EMI Repayment",
  loanSummary,
  emiStatus,
  quickActions,
  upcomingPayments,
  paymentHistory,
  upcomingFooterNote = "Showing upcoming payments.",
  historyFooterNote = "Showing payment history.",
}: EmiRepaymentProps) {
  return (
    <div className="emi-page">
      <h2 className="emi-title">{title}</h2>

      <section className="emi-card">
        <div className="emi-card__header">Loan Summary</div>
        <div className="emi-grid">
          <div>
            <div className="emi-label">Loan ID</div>
            <div className="emi-value">{loanSummary.loanId}</div>
          </div>
          <div>
            <div className="emi-label">Customer</div>
            <div className="emi-value">{loanSummary.customerName}</div>
          </div>
          <div>
            <div className="emi-label">Amount</div>
            <div className="emi-value">{loanSummary.amount}</div>
          </div>
          <div>
            <div className="emi-label">Interest</div>
            <div className="emi-value">{loanSummary.interestRate}</div>
          </div>
          <div>
            <div className="emi-label">Tenure</div>
            <div className="emi-value">{loanSummary.tenure}</div>
          </div>
        </div>
      </section>

      <section className="emi-card">
        <div className="emi-card__header">EMI Status</div>
        <div className="emi-table">
          <div className="emi-table__row">
            <span>Monthly EMI</span>
            <strong>{emiStatus.monthlyEmi}</strong>
            <span>Next Due</span>
            <strong>{emiStatus.nextDueDate}</strong>
            <span>Status</span>
            <strong>{emiStatus.status}</strong>
            <span>Paid On</span>
            <strong>{emiStatus.paidOn}</strong>
          </div>
          <div className="emi-table__row">
            <span>Total Paid</span>
            <strong>{emiStatus.totalPaid}</strong>
            <span>Balance</span>
            <strong>{emiStatus.balance}</strong>
            <span>Overdue</span>
            <strong>{emiStatus.overdue}</strong>
            <span>Remarks</span>
            <strong>{emiStatus.remarks}</strong>
          </div>
        </div>
      </section>

      <section className="emi-card">
        <div className="emi-card__header">Quick Actions</div>
        <div className="emi-actions">
          {quickActions.map((action) => (
            <button
              key={action.label}
              className="emi-action"
              type="button"
              onClick={action.onClick}
            >
              {action.label}
            </button>
          ))}
        </div>
      </section>

      <section className="emi-card">
        <div className="emi-card__header">Upcoming Payments</div>
        <div className="emi-table">
          <div className="emi-table__row emi-table__row--head">
            <span>No</span>
            <span>Due Date</span>
            <span>Principal</span>
            <span>Interest</span>
            <span>Total</span>
          </div>
          {upcomingPayments.map((row) => (
            <div key={row.no} className="emi-table__row">
              <span>{row.no}</span>
              <span>{row.dueDate}</span>
              <span>{row.principal}</span>
              <span>{row.interest}</span>
              <span>{row.total}</span>
            </div>
          ))}
        </div>
        <p className="emi-footer">{upcomingFooterNote}</p>
      </section>

      <section className="emi-card">
        <div className="emi-card__header">Payment History</div>
        <div className="emi-table">
          <div className="emi-table__row emi-table__row--head">
            <span>No</span>
            <span>Due Date</span>
            <span>Paid Date</span>
            <span>Amount</span>
            <span>Status</span>
          </div>
          {paymentHistory.map((row) => (
            <div key={row.no} className="emi-table__row">
              <span>{row.no}</span>
              <span>{row.dueDate}</span>
              <span>{row.paidDate}</span>
              <span>{row.amount}</span>
              <span>{row.status}</span>
            </div>
          ))}
        </div>
        <p className="emi-footer">{historyFooterNote}</p>
      </section>
    </div>
  );
}
