type Props = {
  activeTab: "features" | "eligibility" | "howToAvail";
  content: any;
};

export default function LoanTabContent({ activeTab, content }: Props) {
  return (
    <div className="loan-tab-content">
      <h3>{activeTab === "howToAvail" ? "How To Avail" : activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}</h3>

      <ul>
        {content[activeTab].map((item: string, index: number) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
