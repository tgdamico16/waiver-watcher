"use client";

import {
  getJobStatus,
  getTop10Players,
  Player,
  startJob,
} from "@/actions/actions";
import {
  ParameterSelectors,
  POSITIONS,
  SEASONS,
  WEEKS,
} from "@/components/parameter-selectors";
import { PlayersTable } from "@/components/players-table";
import { Button } from "@/components/ui/button";
import { useState } from "react";

export default function Home() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [position, setPosition] = useState<string>(POSITIONS[0].value);
  const [week, setWeek] = useState<string>(WEEKS[0].value);
  const [season, setSeason] = useState<string>(SEASONS[0].value);
  const [players, setPlayers] = useState<Player[]>([]);

  async function awaitJobCompletion(jobId: string) {
    let jobStatus = await getJobStatus(jobId);
    while (jobStatus != "complete") {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      jobStatus = await getJobStatus(jobId);
    }
  }

  async function handleMakeRequest() {
    setLoading(true);
    try {
      const jobId = await startJob(position, week, season);
      await awaitJobCompletion(jobId);

      const top10Players = await getTop10Players();
      setPlayers(top10Players);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex w-full flex-col items-center p-3">
      <div className="flex flex-col gap-3 items-center">
        <h1 className="text-3xl font-bold h-7">Waiver Watcher</h1>
        <ParameterSelectors
          position={position}
          setPosition={setPosition}
          week={week}
          setWeek={setWeek}
          season={season}
          setSeason={setSeason}
        />
        <Button
          className="w-72 h-9 text-base"
          onClick={handleMakeRequest}
          disabled={loading}
          data-testid="make-request-button"
        >
          Make request
        </Button>
        {error && <p>{error}</p>}
        {players.length > 0 && <PlayersTable players={players} />}
      </div>
    </div>
  );
}
