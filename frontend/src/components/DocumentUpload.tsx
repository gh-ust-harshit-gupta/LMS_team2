interface Props {
  loanType: string;
  onUpload: (docs: string[]) => void;
}

export function DocumentUpload({ loanType, onUpload }: Props) {
  const documentsByLoan: Record<string, string[]> = {
    personal: ["PAN Card", "Salary Slip", "Bank Statement"],
    home: ["Property Documents", "Sale Agreement"],
    vehicle: ["Vehicle Quotation", "Invoice"],
    education: ["Admission Letter", "Fee Structure"]
  };

  const docs = documentsByLoan[loanType] || [];

  return (
    <div className="step-card">
      <h3>Upload Documents</h3>

      {docs.map((doc) => (
        <div key={doc} className="upload-box">
          <label>{doc}</label>
          <input
            type="file"
            onChange={() => onUpload(docs)}
          />
        </div>
      ))}
    </div>
  );
}
