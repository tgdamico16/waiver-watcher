"use client";

import { getJobStatus, getRandomPlayer, startJob } from "@/actions/actions";
import { useState } from "react";

export default function Home() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [randomPlayer, setRandomPlayer] = useState<string | null>(null);

  async function awaitJobCompletion(jobId: string) {
    let jobStatus = await getJobStatus(jobId);
    while (jobStatus != "complete") {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      jobStatus = await getJobStatus(jobId);
    }
  }

  async function handleMakeRequest() {
    setLoading(true);
    console.log("Starting job");
    try {
      const jobId = await startJob();
      await awaitJobCompletion(jobId);
      console.log("Job complete");

      const randomPlayer = await getRandomPlayer();
      setRandomPlayer(randomPlayer);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h1>Waiver Watcher</h1>
      <button
        className="bg-white text-black rounded-2xl px-2 cursor-pointer disabled:bg-gray-600"
        onClick={handleMakeRequest}
        disabled={loading}
        data-testid="make-request-button"
      >
        Make request
      </button>
      <p data-testid="random-player-display">{randomPlayer}</p>
      {error && <p>{error}</p>}
    </div>
  );
}
