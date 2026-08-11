"use client";

import { useState } from "react";

export default function Home() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [randomPlayer, setRandomPlayer] = useState<string | null>(null);

  async function handleMakeRequest() {
    setLoading(true);
    console.log("Calling...");
    const startJobResponse = await fetch(
      `http://${process.env["NEXT_PUBLIC_SERVER_HOST"]}/api/update-statistics`,
    );
    const startJobResult = (await startJobResponse.json()) as
      | {
          status: string;
          job_id: string;
        }
      | {
          status: string;
          error: string;
        };
    console.log("Job started, waiting until job is complete");

    if ("error" in startJobResult) {
      setError(startJobResult.error);
      setLoading(false);
      return;
    }

    const job_id = startJobResult.job_id;

    let job_status = "executing";
    while (job_status != "complete") {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      const jobStatusResponse = await fetch(
        `http://${process.env["NEXT_PUBLIC_SERVER_HOST"]}/api/job-status/${job_id}`,
      );
      const jobStatusResult = (await jobStatusResponse.json()) as
        | {
            status: string;
            job_status: string;
          }
        | {
            status: string;
            error: string;
          };

      if ("error" in jobStatusResult) {
        setError(jobStatusResult.error);
        setLoading(false);
        return;
      }
      job_status = jobStatusResult.job_status;
    }
    console.log("job complete, getting random player");

    const randomPlayerResponse = await fetch(
      `http://${process.env["NEXT_PUBLIC_SERVER_HOST"]}/api/random-player`,
    );
    const randomPlayerResult = (await randomPlayerResponse.json()) as
      | {
          status: string;
          player: string;
        }
      | {
          status: string;
          error: string;
        };

    if ("error" in randomPlayerResult) {
      setError(randomPlayerResult.error);
      setLoading(false);
      return;
    }
    setRandomPlayer(randomPlayerResult.player);

    setLoading(false);
  }

  return (
    <div>
      <h1>Waiver Watcher</h1>
      <button
        className="bg-white text-black rounded-2xl px-2 cursor-pointer disabled:bg-gray-600"
        onClick={handleMakeRequest}
        disabled={loading}
      >
        Make request
      </button>
      {randomPlayer && <p>{randomPlayer}</p>}
      {error && <p>{error}</p>}
    </div>
  );
}
