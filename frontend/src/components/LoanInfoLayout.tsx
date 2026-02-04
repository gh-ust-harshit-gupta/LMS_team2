import LoanSideTabs from "./LoanSideTabs";
import LoanTabContent from "./LoanTabContent";
import "../styles/loanInfo.css";
import { useState } from "react";

type Props = {
  title: string;
  content: {
    features: string[];
    eligibility: string[];
    howToAvail: string[];
  };
};

export default function LoanInfoLayout({ title, content }: Props) {
  const [activeTab, setActiveTab] = useState<"features" | "eligibility" | "howToAvail">("features");

  return (
    <div className="loan-info-container">
      <h2 className="loan-title">{title}</h2>

      <div className="loan-info-body">
        <LoanSideTabs activeTab={activeTab} setActiveTab={setActiveTab} />
        <LoanTabContent activeTab={activeTab} content={content} />
      </div>
    </div>
  );
}
