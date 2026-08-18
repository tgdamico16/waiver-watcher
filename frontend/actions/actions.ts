"use server";

// const API_HOST = "localhost:8000";
const API_HOST = "waiver_watcher_backend:8000";

export type Player = {
  first_name: string;
  last_name: string;
  team: string;
  projected_points: number;
};

function getParams(
  position: string,
  week: string,
  season: string,
): URLSearchParams {
  const params = new URLSearchParams();
  params.append("position", position);
  params.append("week", week);
  params.append("season", season);
  return params;
}

export async function startJob(
  position: string,
  week: string,
  season: string,
): Promise<string> {
  console.log("Starting Job");

  const response = await fetch(
    `http://${API_HOST}/start-job?${getParams(position, week, season)}`,
  );
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

export async function getTop25Players(
  position: string,
  week: string,
  season: string,
): Promise<Player[]> {
  const response = await fetch(
    `http://${API_HOST}/top-25-players?${getParams(position, week, season)}`,
  );
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

export async function getTimestamp(
  position: string,
  week: string,
  season: string,
): Promise<string | null> {
  const response = await fetch(
    `http://${API_HOST}/timestamp?${getParams(position, week, season)}`,
  );
  const result = (await response.json()) as
    | {
        status: string;
        timestamp: string | null;
      }
    | {
        status: string;
        error: string;
      };

  if ("error" in result) {
    console.error(result.error);
    throw new Error(result.error);
  }
  return result.timestamp;
}
