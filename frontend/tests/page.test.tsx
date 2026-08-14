import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Page from "@/app/page";
import { getJobStatus, getRandomPlayer, startJob } from "@/actions/actions";
import { randomUUID } from "crypto";

jest.mock("@/actions/actions", () => ({
  startJob: jest.fn(),
  getJobStatus: jest.fn(),
  getRandomPlayer: jest.fn(),
}));

test("starts job when button is clicked", async () => {
  const testJobId = randomUUID().toString();
  const testRandomPlayer = "Patrick Mahomes";

  (startJob as jest.Mock).mockResolvedValue(testJobId);
  (getJobStatus as jest.Mock).mockResolvedValue("complete");
  (getRandomPlayer as jest.Mock).mockResolvedValue(testRandomPlayer);

  render(<Page />);

  const button = screen.getByTestId("make-request-button");
  const randomPlayerDisplay = screen.getByTestId("random-player-display");

  await fireEvent.click(button);

  await waitFor(() => {
    expect(screen.getByTestId("make-request-button")).toBeEnabled();
  });

  expect(startJob).toHaveBeenCalled();
  expect(getJobStatus).toHaveBeenCalledWith(testJobId);
  expect(getRandomPlayer).toHaveBeenCalled();

  expect(randomPlayerDisplay).toHaveTextContent(testRandomPlayer);
});
