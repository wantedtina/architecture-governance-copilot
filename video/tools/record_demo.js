async (page) => {
  const pause = (milliseconds) => page.waitForTimeout(milliseconds);

  await page.goto("http://localhost:8501/");
  await page.waitForLoadState("domcontentloaded");
  await page.getByRole("heading", { name: "Stage 1 — Review Inputs" }).waitFor();
  await pause(3000);

  await page.getByRole("button", { name: "Load Sample Review" }).click();
  await page.getByText("Synthetic sample loaded · Inputs are editable").waitFor();
  await pause(4000);

  await page.getByRole("tab", { name: "Review Transcript" }).click();
  await page
    .getByRole("textbox", { name: "Synthetic Teams-style Review Transcript" })
    .waitFor();
  await pause(3500);

  await page.getByRole("tab", { name: "Solution Intent" }).click();
  await pause(2500);

  await page.getByRole("button", { name: "Analyze Review" }).click();
  await page.waitForURL(/human-review/);
  await page.getByRole("heading", { name: "Stage 2 — Human Review" }).waitFor();
  await pause(5000);

  await page.getByRole("tab", { name: /Decisions · 1/ }).click();
  await pause(5000);

  await page.getByRole("tab", { name: /Findings · 3/ }).click();
  await pause(5000);
  const firstFindingEvidence = page.getByText("Supporting evidence (3)", {
    exact: false,
  });
  if (await firstFindingEvidence.count()) {
    await firstFindingEvidence.first().click();
    await pause(6000);
  }

  await page.getByRole("tab", { name: /Risks · 1/ }).click();
  await pause(5000);

  await page.getByRole("tab", { name: /Missing Info · 2/ }).click();
  await pause(5000);

  await page.getByRole("tab", { name: /Actions · 2/ }).click();
  await pause(4500);
  const firstVisibleOwner = page
    .locator('input[aria-label="Owner (optional)"]:visible')
    .first();
  await firstVisibleOwner.fill("Taylor Kim");
  await pause(6500);

  await page.getByRole("tab", { name: /Questions · 1/ }).click();
  await pause(4000);
  const questionField = page.getByRole("textbox", { name: "Question" });
  await questionField.focus();
  await page.keyboard.press("Shift+Tab");
  const visibleIncludeCheckbox = page.locator(":focus");
  if (
    (await visibleIncludeCheckbox.getAttribute("aria-label")) !==
    "Include in reviewed record"
  ) {
    throw new Error("Redis inclusion checkbox did not receive focus.");
  }
  await page.keyboard.press("Space");
  await page.waitForTimeout(1000);
  await pause(5500);

  await page
    .getByRole("button", {
      name: "Confirm Reviewed Record & Generate Outputs",
    })
    .click();
  await page.waitForURL(/generated-outputs/);
  await page
    .getByRole("heading", { name: "Stage 3 — Generated Outputs" })
    .waitFor();
  await pause(6500);

  const actionItemsHeading = page.getByRole("heading", {
    name: "Action Items",
    exact: true,
  });
  await actionItemsHeading.scrollIntoViewIfNeeded();
  await pause(5000);

  const adoHeading = page.getByRole("heading", {
    name: "Mock Azure DevOps Work Items",
    exact: true,
  });
  await adoHeading.scrollIntoViewIfNeeded();
  await page
    .getByText("No real Azure DevOps work item has been created.", {
      exact: true,
    })
    .first()
    .waitFor();
  await pause(7000);

  const taylorKim = page.getByText("Taylor Kim", { exact: true });
  if (!(await taylorKim.count())) {
    throw new Error("Taylor Kim was not preserved in generated outputs.");
  }
  if (
    await page
      .getByText("Should Redis be used as a cache?", { exact: true })
      .count()
  ) {
    throw new Error("Redis open question was not excluded from generated output.");
  }

  await page.evaluate(() => window.scrollTo({ top: 0, behavior: "smooth" }));
  await pause(5000);
}
