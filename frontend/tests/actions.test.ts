import {
  startJob,
  getJobStatus,
  getTop25Players,
  getTimestamp,
} from "@/actions/actions";
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

  test("getTop25Players", async () => {
    const position = "qb";
    const week = "1";
    const season = "2026-2027-regular";
    (fetch as jest.Mock).mockResolvedValue({
      json: async () => ({
        status: "success",
        players: [
          {
            first_name: "Patrick",
            last_name: "Mahomes",
            team: "KC",
            projected_points: 100,
          },
        ],
      }),
    });

    const players = await getTop25Players(position, week, season);

    expect(players).toEqual([
      {
        first_name: "Patrick",
        last_name: "Mahomes",
        team: "KC",
        projected_points: 100,
      },
    ]);
    expect(fetch).toHaveBeenCalledWith(
      `http://${API_HOST}/top-25-players?position=${position}&week=${week}&season=${season}`,
    );
  });

  test("getTimestamp", async () => {
    const position = "qb";
    const week = "1";
    const season = "2026-2027-regular";
    const testTimestampStr = "2026-08-18 00:55:09.527152+00:00";
    (fetch as jest.Mock).mockResolvedValue({
      json: async () => ({
        status: "success",
        timestamp: testTimestampStr,
      }),
    });

    const timestamp = await getTimestamp(position, week, season);

    expect(timestamp).toEqual(testTimestampStr);
    expect(fetch).toHaveBeenCalledWith(
      `http://${API_HOST}/timestamp?position=${position}&week=${week}&season=${season}`,
    );
  });
});
