"use server";

// const API_HOST = "localhost:8000";
const API_HOST = "waiver_watcher_backend:8000";

export type Player = {
  id: number;
  first_name: string;
  last_name: string;
  position: string;
  team: string;
  projected_points: number;
};

export async function startJob(
  position: string,
  week: string,
  season: string,
): Promise<string> {
  console.log("Starting Job");

  const params = new URLSearchParams();
  params.append("position", position);
  params.append("week", week);
  params.append("season", season);
  const response = await fetch(`http://${API_HOST}/start-job?${params}`);
  const result = (await response.json()) as
    | {
        status: string;
        job_id: string;
      }
    | {
        status: string;
        error: string;
      };

  if ("error" in result) {
    console.error(result.error);
    throw new Error(result.error);
  }

  console.log("Job started, waiting until job is complete");

  return result.job_id;
}

export async function getJobStatus(
  jobId: string,
): Promise<"nonexistent" | "executing" | "complete"> {
  const response = await fetch(`http://${API_HOST}/job-status/${jobId}`);

  const result = (await response.json()) as
    | {
        status: string;
        job_status: "nonexistent" | "executing" | "complete";
      }
    | {
        status: string;
        error: string;
      };

  if ("error" in result) {
    console.error(result.error);
    throw new Error(result.error);
  }

  return result.job_status;
}

export async function getTop10Players(): Promise<Player[]> {
  const response = await fetch(`http://${API_HOST}/top-10-players`);
  const result = (await response.json()) as
    | {
        status: string;
        players: Player[];
      }
    | {
        status: string;
        error: string;
      };

  if ("error" in result) {
    console.error(result.error);
    throw new Error(result.error);
  }
  return result.players;
}
