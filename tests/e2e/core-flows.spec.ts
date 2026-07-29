import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  page.on("pageerror", (error) => console.error(`BROWSER ERROR: ${error.message}`));
  page.on("console", (message) => { if (message.type() === "error") console.error(`BROWSER CONSOLE: ${message.text()}`); });
});

test("public landing and demo authentication flow", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /Build the career profile/ })).toBeVisible();
  await page.getByRole("link", { name: "Sign in" }).first().click();
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page).toHaveURL(/dashboard/);
  await expect(page.getByRole("heading", { name: /Good evening/ })).toBeVisible();
});

test("resume analysis reviews extraction before report", async ({ page }) => {
  await page.goto("/resume-analysis/new");
  await page.getByRole("button", { name: /Review extraction/ }).click();
  await expect(page).toHaveURL(/resume-analysis\/review/);
  await expect(page.getByRole("heading", { name: /Confirm the facts/ })).toBeVisible();
  await page.getByRole("button", { name: "Confirm and analyse" }).click();
  await expect(page.getByText("Reading documents")).toBeVisible();
  await expect(page).toHaveURL(/resume-analysis\/report/, { timeout: 8000 });
  await expect(page.getByRole("heading", { name: /Strong foundation/ })).toBeVisible();
});

test("jobs can be saved and filtered", async ({ page }) => {
  await page.goto("/jobs");
  await expect(page.getByRole("heading", { name: /Roles matched/ })).toBeVisible();
  await page.getByLabel("Save Growth Analyst").click();
  await page.getByRole("link", { name: /Saved jobs/ }).click();
  await expect(page.getByRole("heading", { name: /Roles you chose/ })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Growth Analyst" })).toBeVisible();
});

test("mobile workspace has no horizontal overflow and opens navigation", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/dashboard");
  await page.getByRole("button", { name: "Open navigation" }).click();
  await expect(page.getByRole("navigation", { name: "Workspace navigation" })).toBeVisible();
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
  expect(overflow).toBe(false);
  await page.keyboard.press("Escape");
  await expect(page.getByRole("button", { name: "Open navigation" })).toBeVisible();
});

test("required viewport matrix has no horizontal overflow", async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== "desktop", "Run the matrix once in Chromium");
  const viewports = [[320,568],[375,667],[390,844],[768,1024],[1024,768],[1280,800],[1440,900],[1920,1080]];
  for (const [width, height] of viewports) {
    await page.setViewportSize({ width, height });
    await page.goto("/dashboard");
    await expect(page.getByRole("heading", { name: /Good evening/ })).toBeVisible();
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
    expect(overflow, `${width}x${height} should not overflow`).toBe(false);
  }
});
