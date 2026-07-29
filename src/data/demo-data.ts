export type Job = { id: string; title: string; company: string; location: string; mode: string; score: number; posted: string; skills: string[]; missing: string[]; saved?: boolean };
export type DemoState = {
  authenticated: boolean;
  onboardingComplete: boolean;
  candidate: { name: string; email: string; headline: string; location: string; role: string; experience: string; skills: string[] };
  activeResume: string;
  activeJobDescription: string;
  savedJobs: string[];
  completedLearning: string[];
  suggestionDecisions: Record<string, "accepted" | "rejected">;
  reducedMotion: boolean;
};

export const initialState: DemoState = {
  authenticated: false,
  onboardingComplete: false,
  candidate: { name: "Aarav Mehta", email: "aarav@example.com", headline: "Product analyst turning evidence into decisions", location: "Bengaluru, India", role: "Product Analyst", experience: "3 years", skills: ["SQL", "Python", "Product analytics", "Data visualization"] },
  activeResume: "Product Analyst Resume v3.pdf",
  activeJobDescription: "Senior Product Analyst · Northstar Labs",
  savedJobs: ["product-analyst"],
  completedLearning: ["sql-foundations"],
  suggestionDecisions: {},
  reducedMotion: false,
};

export const metrics = [
  { label: "ATS alignment", value: "78", suffix: "/100", note: "+6 since v2" },
  { label: "Interview readiness", value: "72", suffix: "%", note: "2 sessions completed" },
  { label: "Learning progress", value: "41", suffix: "%", note: "SQL readiness path" },
  { label: "Relevant roles", value: "12", suffix: "", note: "Based on resume v3" },
];

export const jobs: Job[] = [
  { id: "product-analyst", title: "Product Analyst", company: "Northstar Labs", location: "Bengaluru", mode: "Hybrid", score: 88, posted: "2 days ago", skills: ["SQL", "Product analytics", "Experiments"], missing: ["Amplitude"] },
  { id: "growth-analyst", title: "Growth Analyst", company: "Metric Works", location: "Singapore", mode: "Remote", score: 81, posted: "4 days ago", skills: ["SQL", "Python", "Dashboards"], missing: ["Lifecycle marketing"] },
  { id: "business-analyst", title: "Business Data Analyst", company: "Common Thread", location: "Berlin", mode: "On-site", score: 74, posted: "1 week ago", skills: ["Data visualization", "Stakeholder communication"], missing: ["Tableau", "German"] },
];

export const evidenceRows = [
  { requirement: "Advanced SQL", evidence: "Built cohort and retention analysis using window functions.", status: "Strong match", contribution: "+12", kind: "Extracted Fact" },
  { requirement: "Experiment design", evidence: "Supported A/B test reporting; ownership is not explicit.", status: "Partial match", contribution: "+6", kind: "Deterministic Result" },
  { requirement: "Amplitude", evidence: "This skill was not found in the selected resume.", status: "Not found", contribution: "+0", kind: "Suggested Improvement" },
  { requirement: "Executive communication", evidence: "Presented weekly KPI reviews to product and sales leads.", status: "Strong match", contribution: "+8", kind: "Candidate Confirmed" },
];

export const learningItems = [
  { id: "sql-foundations", title: "SQL query foundations", type: "Practice", duration: "35 min", objective: "Build reliable joins and aggregations" },
  { id: "window-functions", title: "Window functions for product metrics", type: "Lesson", duration: "45 min", objective: "Calculate cohorts, ranks, and rolling metrics" },
  { id: "query-optimization", title: "Practical query optimization", type: "Workshop", duration: "50 min", objective: "Explain and improve slow analytical queries" },
];
