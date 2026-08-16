import { startJob, getJobStatus, getTop10Players } from "@/actions/actions";
import { randomUUID } from "crypto";

const API_HOST = "waiver_watcher_backend:8000";

describe("server actions", () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  test("startJob", async () => {
    const testJobId = randomUUID().toString();
    const position = "qb";
    const week = "1";
    const season = "2026-2027-regular";

    (fetch as jest.Mock).mockResolvedValue({
      json: async () => ({
        status: "success",
        job_id: testJobId,
      }),
    });

    const jobId = await startJob(position, week, season);

    expect(jobId).toBe(testJobId);
    expect(fetch).toHaveBeenCalledWith(
      `http://${API_HOST}/start-job?position=${position}&week=${week}&season=${season}`,
    );
  });

  test("getJobStatus", async () => {
    const testJobId = randomUUID().toString();
    (fetch as jest.Mock).mockResolvedValue({
      json: async () => ({
        status: "success",
        job_status: "complete",
      }),
    });

    const status = await getJobStatus(testJobId);

    expect(status).toBe("complete");
    expect(fetch).toHaveBeenCalledWith(
      `http://${API_HOST}/job-status/${testJobId}`,
    );
  });

  test("getTop10Players", async () => {
    (fetch as jest.Mock).mockResolvedValue({
      json: async () => ({
        status: "ok",
        players: [
          {
            id: 1,
            first_name: "Patrick",
            last_name: "Mahomes",
            position: "QB",
            team: "KC",
            projected_points: 100,
          },
        ],
      }),
    });

    const players = await getTop10Players();

    expect(players).toEqual([
      {
        id: 1,
        first_name: "Patrick",
        last_name: "Mahomes",
        position: "QB",
        team: "KC",
        projected_points: 100,
      },
    ]);
    expect(fetch).toHaveBeenCalledWith(`http://${API_HOST}/top-10-players`);
  });
});
