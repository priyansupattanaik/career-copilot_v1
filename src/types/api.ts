export type CandidateProfile = {
  id: string;
  full_name: string;
  headline: string | null;
  location: string | null;
  current_role: string | null;
  profile_completion: number;
};

export type ApiFailure = {
  error: { code: string; message: string; details: unknown; request_id: string };
};

export type CapabilityFlags = {
  ats_scoring: boolean;
  interview_evaluation: boolean;
  job_recommendations: boolean;
};
