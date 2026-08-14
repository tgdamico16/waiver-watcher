import { startJob, getJobStatus, getRandomPlayer } from "@/actions/actions";
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
    (fetch as jest.Mock).mockResolvedValue({
      json: async () => ({
        status: "success",
        job_id: testJobId,
      }),
    });

    const jobId = await startJob();

    expect(jobId).toBe(testJobId);
    expect(fetch).toHaveBeenCalledWith(`http://${API_HOST}/update-statistics`);
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

  test("getRandomPlayer", async () => {
    (fetch as jest.Mock).mockResolvedValue({
      json: async () => ({
        status: "ok",
        player: "Patrick Mahomes",
      }),
    });

    const player = await getRandomPlayer();

    expect(player).toBe("Patrick Mahomes");
    expect(fetch).toHaveBeenCalledWith(`http://${API_HOST}/random-player`);
  });
});
