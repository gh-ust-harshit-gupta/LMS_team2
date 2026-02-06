interface Props {
  applicant: {
    fullName: string;
    age: number;
    employmentType: string;
    monthlyIncome: number;
    existingEmi: number;
  };
  onChange: (data: any) => void;
}

export default function ApplicantDetails({ applicant, onChange }: Props) {
  return (
    <div className="step-card">
      <h3>Applicant Details</h3>

      <div className="form-group">
        <label>Full Name</label>
        <input
          value={applicant.fullName}
          onChange={(e) => onChange({ ...applicant, fullName: e.target.value })}
        />
      </div>

      <div className="form-group">
        <label>Age</label>
        <input
          type="number"
          value={applicant.age}
          onChange={(e) => onChange({ ...applicant, age: +e.target.value })}
        />
      </div>

      <div className="form-group">
        <label>Employment Type</label>
        <select
          value={applicant.employmentType}
          onChange={(e) =>
            onChange({ ...applicant, employmentType: e.target.value })
          }
        >
          <option value="">Select</option>
          <option value="government">Government</option>
          <option value="private">Private</option>
          <option value="self-employed">Self Employed</option>
        </select>
      </div>

      <div className="form-group">
        <label>Monthly Income (₹)</label>
        <input
          type="number"
          value={applicant.monthlyIncome}
          onChange={(e) =>
            onChange({ ...applicant, monthlyIncome: +e.target.value })
          }
        />
      </div>

      <div className="form-group">
        <label>Existing EMI (₹)</label>
        <input
          type="number"
          value={applicant.existingEmi}
          onChange={(e) =>
            onChange({ ...applicant, existingEmi: +e.target.value })
          }
        />
      </div>
    </div>
  );
}
