async (page) => {
  const pause = (milliseconds) => page.waitForTimeout(milliseconds);

  const clearClickCue = () =>
    page.evaluate(() => document.getElementById("agc-video-click-cue")?.remove());

  const showClickCue = async (locator, label) => {
    await locator.scrollIntoViewIfNeeded();
    const box = await locator.boundingBox();
    if (!box) {
      throw new Error(`Unable to position click cue for ${label}.`);
    }
    await page.evaluate(
      ({ box, label }) => {
        document.getElementById("agc-video-click-cue")?.remove();
        const cue = document.createElement("div");
        cue.id = "agc-video-click-cue";
        cue.style.cssText = [
          "position:fixed",
          `left:${Math.max(8, box.x - 6)}px`,
          `top:${Math.max(8, box.y - 6)}px`,
          `width:${box.width + 12}px`,
          `height:${box.height + 12}px`,
          "border:4px solid #ff4b4b",
          "border-radius:10px",
          "box-shadow:0 0 0 5px rgba(255,75,75,.22),0 8px 24px rgba(6,29,51,.28)",
          "pointer-events:none",
          "z-index:2147483647",
          "box-sizing:border-box",
        ].join(";");

        const badge = document.createElement("div");
        badge.textContent = `CLICK · ${label}`;
        badge.style.cssText = [
          "position:absolute",
          "right:0",
          "bottom:calc(100% + 8px)",
          "background:#ff4b4b",
          "color:white",
          "font:700 15px/1.2 Arial,sans-serif",
          "letter-spacing:.02em",
          "padding:7px 11px",
          "border-radius:7px",
          "white-space:nowrap",
        ].join(";");
        cue.appendChild(badge);

        const pulse = document.createElement("div");
        pulse.style.cssText = [
          "position:absolute",
          "left:50%",
          "top:50%",
          "width:22px",
          "height:22px",
          "transform:translate(-50%,-50%)",
          "border:5px solid white",
          "border-radius:50%",
          "background:#ff4b4b",
          "box-shadow:0 0 0 8px rgba(255,75,75,.35)",
        ].join(";");
        cue.appendChild(pulse);
        document.body.appendChild(cue);
      },
      { box, label },
    );
    await pause(700);
  };

  const clickWithCue = async (locator, label) => {
    await showClickCue(locator, label);
    await locator.click();
    await pause(350);
    await clearClickCue();
  };

  const scrollPreviewContent = async () => {
    const panel = page.locator('[role="tabpanel"]:visible');
    await panel.waitFor();
    await panel.scrollIntoViewIfNeeded();
    await pause(500);
    const range = await panel.evaluate((element) => {
      const rect = element.getBoundingClientRect();
      const top = Math.max(0, window.scrollY + rect.top - 170);
      const bottom = Math.max(
        top,
        window.scrollY + rect.bottom - window.innerHeight + 140,
      );
      return { top, bottom };
    });
    await page.evaluate(
      (top) => window.scrollTo({ top, behavior: "smooth" }),
      range.top,
    );
    await pause(900);
    for (const progress of [0.34, 0.67, 1]) {
      const destination = range.top + (range.bottom - range.top) * progress;
      await page.evaluate(
        (top) => window.scrollTo({ top, behavior: "smooth" }),
        destination,
      );
      await pause(950);
    }
  };

  await page.waitForLoadState("domcontentloaded");
  await page
    .getByRole("heading", { name: "Stage 1 — Project Context" })
    .waitFor();
  await pause(3500);

  await clickWithCue(
    page.getByRole("button", { name: "Open Demonstration Project" }),
    "Open project",
  );
  await page
    .getByText("ADO Workitem - Solution Intent 12658902", { exact: true })
    .waitFor();
  await pause(3500);

  await clickWithCue(
    page.getByText("Inspect selected source previews"),
    "Inspect source previews",
  );
  await scrollPreviewContent();

  await clickWithCue(
    page.getByRole("tab", { name: "Repository" }),
    "Repository tab",
  );
  await scrollPreviewContent();

  await clickWithCue(page.getByRole("tab", { name: "Evidence" }), "Evidence tab");
  await scrollPreviewContent();

  await clickWithCue(
    page.getByRole("tab", { name: "Governance Metadata" }),
    "Governance metadata tab",
  );
  await scrollPreviewContent();

  await clickWithCue(
    page.getByRole("button", { name: "Refresh Context" }),
    "Refresh context",
  );
  await pause(2500);

  await clickWithCue(
    page.getByRole("button", { name: "Confirm Context & Continue" }),
    "Confirm context",
  );
  await page
    .getByRole("heading", { name: "Stage 2 — Draft Solution Intent" })
    .waitFor();
  await pause(3500);

  await clickWithCue(
    page.getByRole("button", { name: "Generate SI Draft" }),
    "Generate SI draft",
  );
  await page
    .getByRole("textbox", { name: "Human-reviewed SI draft" })
    .waitFor();
  await pause(5500);

  await clickWithCue(
    page.getByRole("button", {
      name: "Confirm SI Draft & Continue to Review",
    }),
    "Confirm SI draft",
  );
  await page
    .getByRole("heading", { name: "Stage 3 — Review Inputs" })
    .waitFor();
  await pause(3500);

  await clickWithCue(
    page.getByRole("button", { name: "Load Sample Transcript & Metadata" }),
    "Load review transcript",
  );
  await page
    .getByText("Confirmed SI + review companions ready")
    .waitFor();
  await pause(4000);

  await clickWithCue(
    page.getByRole("tab", { name: "Review Transcript" }),
    "Review transcript tab",
  );
  await page
    .getByRole("textbox", { name: "Teams-style Review Transcript" })
    .waitFor();
  await pause(3500);

  await clickWithCue(
    page.getByRole("tab", { name: "Solution Intent" }),
    "Solution Intent tab",
  );
  await pause(2500);

  await clickWithCue(
    page.getByRole("button", { name: "Analyze Review" }),
    "Analyze review",
  );
  await page.waitForURL(/human-review/);
  await page.getByRole("heading", { name: "Stage 4 — Human Review" }).waitFor();
  await pause(5000);

  await clickWithCue(
    page.getByRole("tab", { name: /Decisions · 1/ }),
    "Decisions tab",
  );
  await pause(5000);

  await clickWithCue(
    page.getByRole("tab", { name: /Findings · 3/ }),
    "Findings tab",
  );
  await pause(5000);
  const firstFindingEvidence = page.getByText("Supporting evidence (3)", {
    exact: false,
  });
  if (await firstFindingEvidence.count()) {
    await clickWithCue(firstFindingEvidence.first(), "Supporting evidence");
    await pause(6000);
  }

  await clickWithCue(
    page.getByRole("tab", { name: /Risks · 1/ }),
    "Risks tab",
  );
  await pause(5000);

  await clickWithCue(
    page.getByRole("tab", { name: /Missing Info · 2/ }),
    "Missing information tab",
  );
  await pause(5000);

  await clickWithCue(
    page.getByRole("tab", { name: /Actions · 2/ }),
    "Actions tab",
  );
  await pause(4500);
  const firstVisibleOwner = page
    .locator('input[aria-label="Owner (optional)"]:visible')
    .first();
  await showClickCue(firstVisibleOwner, "Edit action owner");
  await firstVisibleOwner.fill("Taylor Kim");
  await clearClickCue();
  await pause(6500);

  await clickWithCue(
    page.getByRole("tab", { name: /Questions · 1/ }),
    "Open questions tab",
  );
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
  await showClickCue(visibleIncludeCheckbox, "Exclude Redis question");
  await page.keyboard.press("Space");
  await clearClickCue();
  await page.waitForTimeout(1000);
  await pause(5500);

  await clickWithCue(
    page.getByRole("button", {
      name: "Confirm Reviewed Record & Generate Outputs",
    }),
    "Generate outputs",
  );
  await page.waitForURL(/generated-outputs/);
  await page
    .getByRole("heading", { name: "Stage 5 — Generated Outputs" })
    .waitFor();
  await pause(6500);

  const actionItemsHeading = page.getByRole("heading", {
    name: "Action Items",
    exact: true,
  });
  await actionItemsHeading.scrollIntoViewIfNeeded();
  await pause(5000);

  const adoHeading = page.getByRole("heading", {
    name: "Azure DevOps Work Item Previews",
    exact: true,
  });
  await adoHeading.scrollIntoViewIfNeeded();
  await page
    .getByText("Preview only · No work items were submitted to Azure DevOps.", {
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
