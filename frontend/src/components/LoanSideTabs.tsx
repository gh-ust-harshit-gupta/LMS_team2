type Props = {
  activeTab: string;
  setActiveTab: (tab: any) => void;
};

export default function LoanSideTabs({ activeTab, setActiveTab }: Props) {
  return (
    <div className="loan-tabs">
      {["features", "eligibility", "howToAvail"].map(tab => (
        <div
          key={tab}
          className={`loan-tab ${activeTab === tab ? "active" : ""}`}
          onClick={() => setActiveTab(tab)}
        >
          {tab === "howToAvail" ? "How To Avail" : tab.charAt(0).toUpperCase() + tab.slice(1)}
        </div>
      ))}
    </div>
  );
}
