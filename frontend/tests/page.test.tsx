import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Page from "@/app/page";
import { getJobStatus, getTop10Players, startJob } from "@/actions/actions";
import { randomUUID } from "crypto";

jest.mock("@/actions/actions", () => ({
  startJob: jest.fn(),
  getJobStatus: jest.fn(),
  getTop10Players: jest.fn(),
}));

test("starts job when button is clicked", async () => {
  const testJobId = randomUUID().toString();
  const testTop10Players = [
    {
      id: 1,
      first_name: "Patrick",
      last_name: "Mahomes",
      position: "QB",
      team: "KC",
      projected_points: 100,
    },
  ];

  (startJob as jest.Mock).mockResolvedValue(testJobId);
  (getJobStatus as jest.Mock).mockResolvedValue("complete");
  (getTop10Players as jest.Mock).mockResolvedValue(testTop10Players);

  render(<Page />);

  const button = screen.getByTestId("make-request-button");

  await fireEvent.click(button);

  await waitFor(() => {
    expect(screen.getByTestId("make-request-button")).toBeEnabled();
  });

  expect(startJob).toHaveBeenCalled();
  expect(getJobStatus).toHaveBeenCalledWith(testJobId);
  expect(getTop10Players).toHaveBeenCalled();
  expect(screen.getByText("Patrick Mahomes")).toBeInTheDocument();
});
