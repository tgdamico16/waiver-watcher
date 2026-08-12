"use server";

const API_HOST = "localhost:8000";

export async function startJob(): Promise<string> {
  const response = await fetch(`http://${API_HOST}/update-statistics`);
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
): Promise<"executing" | "complete"> {
  const response = await fetch(`http://${API_HOST}/job-status/${jobId}`);

  const result = (await response.json()) as
    | {
        status: string;
        job_status: "executing" | "complete";
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

export async function getRandomPlayer(): Promise<string> {
  const response = await fetch(`http://${API_HOST}/random-player`);
  const result = (await response.json()) as
    | {
        status: string;
        player: string;
      }
    | {
        status: string;
        error: string;
      };

  if ("error" in result) {
    console.error(result.error);
    throw new Error(result.error);
  }
  return result.player;
}
