"use client";

import {
  getJobStatus,
  getTimestamp,
  getTop25Players,
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
  const [fetchingData, setFetchingData] = useState<boolean>(false);
  const [callingAPI, setCallingAPI] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [position, setPosition] = useState<string>(POSITIONS[0].value);
  const [week, setWeek] = useState<string>(WEEKS[0].value);
  const [season, setSeason] = useState<string>(SEASONS[0].value);
  const [players, setPlayers] = useState<Player[]>([]);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  async function awaitJobCompletion(jobId: string) {
    let jobStatus = await getJobStatus(jobId);
    while (jobStatus != "complete") {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      jobStatus = await getJobStatus(jobId);
    }
  }

  async function handleGetData(performInitialQuery: boolean = true) {
    setFetchingData(true);
    try {
      let newPlayers = performInitialQuery
        ? await getTop25Players(position, week, season)
        : [];
      let newTimestamp = performInitialQuery
        ? await getTimestamp(position, week, season)
        : null;

      if (newPlayers.length < 1) {
        setCallingAPI(true);
        const jobId = await startJob(position, week, season);
        await awaitJobCompletion(jobId);
        newPlayers = await getTop25Players(position, week, season);
        newTimestamp = await getTimestamp(position, week, season);
      }

      setPlayers(newPlayers);
      setLastUpdated(newTimestamp ? new Date(newTimestamp) : null);
    } catch (e) {
      setError(String(e));
    } finally {
      setFetchingData(false);
      setCallingAPI(false);
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
          className="w-74 h-9 text-base cursor-pointer"
          onClick={() => handleGetData()}
          disabled={fetchingData || callingAPI}
          data-testid="make-request-button"
        >
          {callingAPI
            ? "Calling API, this may take a minute..."
            : fetchingData
              ? "Loading..."
              : "Go"}
        </Button>
        {error && <p>{error}</p>}
        {players.length > 0 && <PlayersTable players={players} />}
        {lastUpdated && (
          <div className="flex items-center gap-2">
            <p>Last updated: {lastUpdated.toLocaleString()}</p>
            <Button
              variant="outline"
              className="cursor-pointer"
              onClick={() => handleGetData(false)}
              disabled={fetchingData || callingAPI}
            >
              Update
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
