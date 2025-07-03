// Function to analyze resume pasted in textarea
async function analyzeResume() {
  const resume = document.getElementById("resumeInput").value.trim();
  const resultsSection = document.getElementById("results");
  const summaryEl = document.getElementById("summary");
  const rolesList = document.getElementById("rolesList");
  const questionsBlock = document.getElementById("questionsBlock");
  const tipEl = document.getElementById("tip");

  // Clear previous results
  summaryEl.textContent = "";
  rolesList.innerHTML = "";
  questionsBlock.innerHTML = "";
  tipEl.textContent = "";
  resultsSection.classList.add("hidden");

  if (!resume) {
    alert("⚠️ Please enter your resume text first!");
    return;
  }

  // Show feedback
  summaryEl.textContent = "Analyzing your resume with AI... please wait ⏳";
  resultsSection.classList.remove("hidden");

  try {
    const response = await fetch("/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ resume })
    });

    const data = await response.json();

    if (data.result) {
      const raw = data.result;

      // Attempt to split result into structured parts (based on numbering)
      const parts = raw.split(/\d\.\s+/); // Ex: 1. Summary, 2. Roles, etc.

      if (parts.length >= 5) {
        // Part 1: Summary
        summaryEl.textContent = parts[1]?.trim();

        // Part 2: Suggested Roles
        const roles = parts[2]
          .split("\n")
          .filter(line => line.trim())
          .slice(0, 3);

        roles.forEach(role => {
          const li = document.createElement("li");
          li.textContent = role.replace(/^\-/, '').trim();
          rolesList.appendChild(li);
        });

        // Part 3: Interview Questions
        const questions = parts[3].split(/Q\d+:/i).slice(1);

        questions.forEach(q => {
          const block = document.createElement("div");
          block.className = "question-block";
          block.innerHTML = `<strong>Q:</strong> ${q.trim().replace(/\n/g, "<br>")}`;
          questionsBlock.appendChild(block);
        });

        // Part 4: Resume Tip
        tipEl.textContent = parts[4]?.trim();
      } else {
        // Fallback if structure fails
        summaryEl.textContent = raw;
      }

    } else {
      summaryEl.textContent = "❌ Error: " + (data.error || "No response received.");
    }

  } catch (error) {
    summaryEl.textContent = "❌ Something went wrong while analyzing resume.";
    console.error("Error:", error);
  }
}
 