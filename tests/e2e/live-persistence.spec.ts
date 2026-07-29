import { readFileSync } from "node:fs";
import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import { expect, test } from "@playwright/test";

function readEnvironment(path: string) {
  return Object.fromEntries(
    readFileSync(path, "utf8")
      .split(/\r?\n/)
      .filter((line) => /^[A-Za-z_][A-Za-z0-9_]*=/.test(line))
      .map((line) => {
        const separator = line.indexOf("=");
        return [line.slice(0, separator), line.slice(separator + 1)];
      }),
  );
}

test.describe("live Supabase persistence", () => {
  test.describe.configure({ mode: "serial" });
  const backendEnvironment = readEnvironment("backend/.env");
  const projectUrl = backendEnvironment.SUPABASE_URL;
  const adminKey = backendEnvironment.SUPABASE_SERVICE_ROLE_KEY || backendEnvironment.SUPABASE_SECRET_KEY;
  const suffix = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  const email = `audit-browser-${suffix}@example.invalid`;
  const password = `Audit-${suffix}-A1!`;
  let admin: SupabaseClient;
  let userId = "";

  test.beforeAll(async () => {
    expect(projectUrl, "SUPABASE_URL must be configured").toBeTruthy();
    expect(adminKey, "A server-only admin key must be configured").toBeTruthy();
    admin = createClient(projectUrl, adminKey, {
      auth: { autoRefreshToken: false, persistSession: false },
    });
    const { data, error } = await admin.auth.admin.createUser({
      email,
      password,
      email_confirm: true,
      user_metadata: { full_name: "Audit Browser" },
    });
    if (error) throw error;
    userId = data.user.id;
  });

  test.afterAll(async () => {
    if (admin && userId) await admin.auth.admin.deleteUser(userId);
  });

  test("profile, settings, and job description persist through the real UI", async ({ page }) => {
    test.setTimeout(90_000);
    const browserErrors: string[] = [];
    page.on("pageerror", (error) => browserErrors.push(error.message));
    page.on("console", (message) => {
      if (message.type() === "error") browserErrors.push(message.text());
    });

    await page.goto("/sign-in");
    await page.getByLabel("Email").fill(email);
    await page.getByLabel("Password").fill(password);
    await page.getByRole("button", { name: "Sign in" }).click();
    await expect(page).toHaveURL(/\/dashboard$/);

    await page.goto("/onboarding");
    await page.getByLabel("Full name").fill("Audit Candidate Persisted");
    await page.getByLabel("Professional headline").fill("Evidence Engineer");
    await page.getByLabel("Phone").fill("+91 9000000000");
    await page.getByLabel("Location").fill("Pune");
    await page.getByLabel("Current role").fill("Data Analyst");
    await page.getByLabel("Bio").fill("Temporary browser audit profile.");
    await page.getByRole("button", { name: "Save profile" }).click();
    await expect(page).toHaveURL(/\/dashboard$/);
    await expect(page.getByRole("heading", { name: /Welcome, Audit\./ })).toBeVisible();

    await page.goto("/settings/profile");
    await expect(page.getByLabel("Headline")).toHaveValue("Evidence Engineer");
    await page.getByLabel("Headline").fill("Verified Evidence Engineer");
    await page.getByRole("button", { name: "Save profile" }).click();
    await expect(page.getByRole("status")).toHaveText("Profile saved.");
    await page.reload();
    await expect(page.getByLabel("Headline")).toHaveValue("Verified Evidence Engineer");

    await page.goto("/settings/privacy");
    await page.getByLabel("resume processing consent").check();
    await page.getByRole("button", { name: "Save settings" }).click();
    await expect(page.getByRole("status")).toHaveText("Settings saved.");
    await page.reload();
    await expect(page.getByLabel("resume processing consent")).toBeChecked();

    await page.goto("/resume-analysis/new");
    await page.getByLabel("Paste text").fill(
      "Evidence Engineer role requiring Python, SQL, accessibility, and secure data persistence.",
    );
    await page.getByRole("button", { name: "Store job description" }).click();
    await expect(page.getByRole("status")).toContainText("Job description stored for review");

    for (const [width, height] of [
      [320, 568],
      [375, 667],
      [390, 844],
      [768, 1024],
      [1024, 768],
      [1280, 800],
      [1440, 900],
      [1920, 1080],
    ]) {
      await page.setViewportSize({ width, height });
      await page.goto("/dashboard");
      const overflow = await page.evaluate(
        () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
      );
      expect(overflow, `${width}x${height} authenticated dashboard should not overflow`).toBe(false);
    }

    const profile = await admin.from("profiles").select("full_name,headline,phone,location,current_role,bio").eq("id", userId).single();
    expect(profile.error).toBeNull();
    expect(profile.data).toMatchObject({
      full_name: "Audit Candidate Persisted",
      headline: "Verified Evidence Engineer",
      phone: "+91 9000000000",
      location: "Pune",
      current_role: "Data Analyst",
      bio: "Temporary browser audit profile.",
    });
    const privacy = await admin.from("privacy_preferences").select("resume_processing_consent").eq("user_id", userId).single();
    expect(privacy.data?.resume_processing_consent).toBe(true);
    const descriptions = await admin.from("job_descriptions").select("id,user_id").eq("user_id", userId);
    expect(descriptions.data).toHaveLength(1);

    await page.goto("/settings/account");
    await page.getByRole("button", { name: "Logout", exact: true }).click();
    await expect(page).toHaveURL(/\/$/);
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/sign-in/);
    expect(browserErrors).toEqual([]);
  });
});
