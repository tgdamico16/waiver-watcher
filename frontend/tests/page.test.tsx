import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Page from "@/app/page";
import {
  getJobStatus,
  getTimestamp,
  getTop25Players,
  startJob,
} from "@/actions/actions";
import { randomUUID } from "crypto";

jest.mock("@/actions/actions", () => ({
  startJob: jest.fn(),
  getJobStatus: jest.fn(),
  getTop25Players: jest.fn(),
  getTimestamp: jest.fn(),
}));

test("button is clicked, data already in database", async () => {
  const testTop25Players = [
    {
      first_name: "Patrick",
      last_name: "Mahomes",
      team: "KC",
      projected_points: 100,
    },
  ];
  const testTimestampStr = "2026-08-18 00:55:09.527152+00:00";

  (getTop25Players as jest.Mock).mockResolvedValue(testTop25Players);
  (getTimestamp as jest.Mock).mockResolvedValue(testTimestampStr);

  render(<Page />);

  const button = screen.getByTestId("make-request-button");

  await fireEvent.click(button);

  await waitFor(() => {
    expect(screen.getByTestId("make-request-button")).toBeEnabled();
  });

  expect(getTop25Players).toHaveBeenCalled();
  expect(getTimestamp).toHaveBeenCalled();
  expect(screen.getByText("Patrick Mahomes")).toBeInTheDocument();
});

test("button is clicked, data not already in database", async () => {
  const testJobId = randomUUID().toString();
  const testTop25Players = [
    {
      first_name: "Patrick",
      last_name: "Mahomes",
      team: "KC",
      projected_points: 100,
    },
  ];
  const testTimestampStr = "2026-08-18 00:55:09.527152+00:00";

  (getTop25Players as jest.Mock)
    .mockResolvedValueOnce([])
    .mockResolvedValueOnce(testTop25Players);
  (getTimestamp as jest.Mock).mockResolvedValue(testTimestampStr);
  (startJob as jest.Mock).mockResolvedValue(testJobId);
  (getJobStatus as jest.Mock).mockResolvedValue("complete");

  render(<Page />);

  const button = screen.getByTestId("make-request-button");

  await fireEvent.click(button);

  await waitFor(() => {
    expect(screen.getByTestId("make-request-button")).toBeEnabled();
  });

  expect(startJob).toHaveBeenCalled();
  expect(getJobStatus).toHaveBeenCalledWith(testJobId);
  expect(getTop25Players).toHaveBeenCalled();
  expect(screen.getByText("Patrick Mahomes")).toBeInTheDocument();
});
