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

function makeDocxFile(name = "resume.docx") {
  return new File(["docx-bytes"], name, {
    type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  });
}

describe("new ATS upload flow", () => {
  beforeEach(() => {
    mocks.apiRequest.mockReset();
    mocks.push.mockReset();
  });

  it("shows select inputs and disabled Proceed until both sides are ready", () => {
    render(<NewAnalysis />);
    expect(screen.getByRole("heading", { name: "1. Resume" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "2. Job description" })).toBeVisible();
    expect(screen.getByRole("button", { name: "Proceed" })).toBeDisabled();
    expect(screen.queryByRole("button", { name: "Upload resume" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Store job description" })).toBeNull();
  });

  it("on Proceed uploads resume then stores JD then opens review", async () => {
    mocks.apiRequest.mockImplementation((path: string, init?: RequestInit) => {
      if (path === "/resumes" && init?.method === "POST") {
        return Promise.resolve({
          resume: { id: "r1", title: "resume", is_active: true, created_at: "2026-01-01" },
          version: {
            id: "v1",
            resume_id: "r1",
            version_number: 1,
            source_type: "uploaded",
            extraction_status: "review_required",
            structured_content: { sections: { skills: ["Python"] } },
            created_at: "2026-01-01",
          },
        });
      }
      if (path === "/job-descriptions" && init?.method === "POST") {
        return Promise.resolve({
          id: "jd-1",
          title: "Evidence Engineer",
          role_title: "Evidence Engineer",
          company: null,
          extraction_status: "review_required",
          structured_content: { sections: { requirements: ["Python", "SQL"] } },
          raw_text: "Evidence Engineer role requiring Python, SQL, accessibility, and secure data persistence.",
        });
      }
      throw new Error(`Unexpected request: ${path}`);
    });

    render(<NewAnalysis />);

    const resumeInput = screen.getByLabelText("Resume file") as HTMLInputElement;
    fireEvent.change(resumeInput, { target: { files: [makeDocxFile()] } });
    fireEvent.change(screen.getByLabelText("Paste text"), {
      target: {
        value: "Evidence Engineer role requiring Python, SQL, accessibility, and secure data persistence.",
      },
    });

    const proceed = screen.getByRole("button", { name: "Proceed" });
    await waitFor(() => expect(proceed).toBeEnabled());
    fireEvent.click(proceed);

    await waitFor(() =>
      expect(mocks.apiRequest).toHaveBeenCalledWith("/resumes", expect.objectContaining({ method: "POST" })),
    );
    await waitFor(() =>
      expect(mocks.apiRequest).toHaveBeenCalledWith(
        "/job-descriptions",
        expect.objectContaining({ method: "POST" }),
      ),
    );
    expect(await screen.findByRole("heading", { name: "Confirm extracted resume and JD" })).toBeVisible();
  });
});
