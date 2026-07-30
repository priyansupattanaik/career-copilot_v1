import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { NewAnalysis } from "./resume-flow";

const mocks = vi.hoisted(() => ({
  apiRequest: vi.fn(),
  push: vi.fn(),
}));

vi.mock("@/lib/api/client", () => ({ apiRequest: mocks.apiRequest }));
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mocks.push }),
  useParams: () => ({}),
  useSearchParams: () => new URLSearchParams(),
}));

describe("new ATS upload flow", () => {
  beforeEach(() => {
    mocks.apiRequest.mockReset();
    mocks.push.mockReset();
  });

  it("stores a pasted job description through the API", async () => {
    mocks.apiRequest.mockResolvedValueOnce({
      id: "jd-1",
      title: "Job description",
      extraction_status: "review_required",
      structured_content: { sections: { requirements: ["Python", "SQL"] } },
      raw_text: "Evidence Engineer role requiring Python, SQL, accessibility, and secure data persistence.",
    });

    render(<NewAnalysis />);
    fireEvent.change(screen.getByLabelText("Paste text"), {
      target: {
        value: "Evidence Engineer role requiring Python, SQL, accessibility, and secure data persistence.",
      },
    });
    fireEvent.click(screen.getByRole("button", { name: "Store job description" }));

    await waitFor(() =>
      expect(mocks.apiRequest).toHaveBeenCalledWith(
        "/job-descriptions",
        expect.objectContaining({ method: "POST" }),
      ),
    );
    expect(await screen.findByText(/Job description stored/i)).toBeVisible();
  });

  it("shows resume and JD upload options for new analysis", () => {
    render(<NewAnalysis />);
    expect(screen.getByRole("heading", { name: "Resume upload" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "Job description" })).toBeVisible();
    expect(screen.getByRole("button", { name: "Upload resume" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Upload PDF/DOCX" })).toBeVisible();
  });
});
