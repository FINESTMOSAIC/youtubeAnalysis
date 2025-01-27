import puppeteer from "puppeteer";
import { spawn } from "child_process";
import path from "path"; // Import path to resolve script location dynamically

export async function GET(req) {
  const { searchParams } = new URL(req.url);
  const videoUrl = searchParams.get("videoUrl");

  if (!videoUrl) {
    return new Response(
      JSON.stringify({ error: "Video URL is required" }),
      { status: 400 }
    );
  }

  try {
    // Launch Puppeteer
    const browser = await puppeteer.launch({
      headless: "new", // Set to true if you need strict headless mode
    });
    const page = await browser.newPage();

    // Navigate to the YouTube video URL
    await page.goto(videoUrl, { waitUntil: "networkidle2" });

    // Wait for the comments section to load
    await page.waitForSelector("ytd-comments");

    // Scroll to load comments
    await autoScroll(page);

    // Extract comments
    const comments = await page.evaluate(() => {
      const commentNodes = document.querySelectorAll("#content-text");
      return Array.from(commentNodes).map((node) => node.innerText.trim());
    });

    // Close the browser
    await browser.close();

    // Run Python script with comments
    const pythonScriptPath = path.join(process.cwd(), "src/scripts", "sentiment_analysis.py"); // Dynamic path
    const sentimentData = await runPythonScript(pythonScriptPath, comments);

    return new Response(
      JSON.stringify(sentimentData),
      { status: 200 }
    );
  } catch (error) {
    console.error("Error scraping YouTube:", error.message);
    return new Response(
      JSON.stringify({ error: "Failed to scrape YouTube comments." }),
      { status: 500 }
    );
  }
}

// Helper function to scroll the page
async function autoScroll(page) {
  await page.evaluate(async () => {
    await new Promise((resolve) => {
      let totalHeight = 0;
      const distance = 100;
      const timer = setInterval(() => {
        const scrollHeight = document.documentElement.scrollHeight;
        window.scrollBy(0, distance);
        totalHeight += distance;

        if (totalHeight >= scrollHeight) {
          clearInterval(timer);
          resolve();
        }
      }, 100);
    });
  });
}

// Function to execute Python script and get sentiment analysis
function runPythonScript(pythonScriptPath, comments) {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn("python", [pythonScriptPath]);

    let output = "";
    let errorOutput = "";

    pythonProcess.stdin.write(JSON.stringify(comments));
    pythonProcess.stdin.end();

    pythonProcess.stdout.on("data", (data) => {
      output += data.toString();
    });

    pythonProcess.stderr.on("data", (data) => {
      errorOutput += data.toString();
    });

    pythonProcess.on("close", (code) => {
      if (code === 0) {
        try {
          resolve(JSON.parse(output));
        } catch (e) {
          reject(new Error("Failed to parse Python script output"));
        }
      } else {
        reject(new Error(errorOutput || "Unknown error occurred in Python script"));
      }
    });
  });
}
