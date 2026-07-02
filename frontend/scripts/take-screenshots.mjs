import { chromium } from "playwright";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const screenshotsDir = path.resolve(__dirname, "../../screenshots");

const BASE_URL = "http://localhost:5173";
const DEMO_EMAIL = "demo@savvyboard.app";
const DEMO_PASSWORD = "demo123";

async function takeScreenshots() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();

  const screenshot = async (name, url) => {
    await page.goto(url, { waitUntil: "networkidle" });
    await page.screenshot({
      path: path.join(screenshotsDir, name),
      fullPage: false,
    });
    console.log(`Screenshot saved: ${name}`);
  };

  await screenshot("landing.png", `${BASE_URL}/`);
  await screenshot("public-workspace.png", `${BASE_URL}/w/savvyboard-demo`);
  await screenshot("public-board.png", `${BASE_URL}/w/savvyboard-demo/boards/feature-requests`);
  await screenshot("public-roadmap.png", `${BASE_URL}/w/savvyboard-demo/roadmap`);
  await screenshot("public-changelog.png", `${BASE_URL}/w/savvyboard-demo/changelog`);

  // Admin login
  await page.goto(`${BASE_URL}/login`, { waitUntil: "networkidle" });
  await page.fill('input[type="email"]', DEMO_EMAIL);
  await page.fill('input[type="password"]', DEMO_PASSWORD);
  await page.click('button[type="submit"]');
  await page.waitForURL("**/admin", { waitUntil: "networkidle" });
  await page.screenshot({ path: path.join(screenshotsDir, "admin-workspaces.png"), fullPage: false });
  console.log("Screenshot saved: admin-workspaces.png");

  // Fetch workspace id and navigate to dashboard directly
  const token = await page.evaluate(() => localStorage.getItem("access_token"));
  console.log("Token retrieved:", token ? "yes" : "no");
  const response = await page.evaluate(async (authToken) => {
    const res = await fetch("/api/v1/workspaces/", {
      headers: { Authorization: `Bearer ${authToken}` },
    });
    const text = await res.text();
    return { status: res.status, body: text };
  }, token);
  console.log("Workspaces response:", response.status, response.body.slice(0, 200));
  const workspaces = response.status === 200 ? JSON.parse(response.body) : [];
  const workspaceId = workspaces[0]?.id;
  if (workspaceId) {
    await page.goto(`${BASE_URL}/admin/workspaces/${workspaceId}`, { waitUntil: "networkidle" });
    await page.screenshot({ path: path.join(screenshotsDir, "admin-dashboard.png"), fullPage: false });
    console.log("Screenshot saved: admin-dashboard.png");

    await page.goto(`${BASE_URL}/admin/workspaces/${workspaceId}/boards`, { waitUntil: "networkidle" });
    await page.screenshot({ path: path.join(screenshotsDir, "admin-boards.png"), fullPage: false });
    console.log("Screenshot saved: admin-boards.png");

    await page.goto(`${BASE_URL}/admin/workspaces/${workspaceId}/feedback`, { waitUntil: "networkidle" });
    await page.screenshot({ path: path.join(screenshotsDir, "admin-feedback.png"), fullPage: false });
    console.log("Screenshot saved: admin-feedback.png");
  }

  await browser.close();
}

takeScreenshots().catch((err) => {
  console.error(err);
  process.exit(1);
});
