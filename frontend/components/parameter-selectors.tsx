import { Dispatch, SetStateAction } from "react";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";

export const POSITIONS = [
  { label: "QB", value: "qb" },
  { label: "RB", value: "rb" },
  { label: "WR", value: "wr" },
  { label: "TE", value: "te" },
  { label: "K", value: "k" },
];
export const WEEKS = Array.from({ length: 18 }, (_, i) => ({
  label: `${i + 1}`,
  value: `${i + 1}`,
}));
export const SEASONS = [
  {
    label: "2026-2027",
    value: "2026-2027-regular",
  },
  {
    label: "2025-2026",
    value: "2025-2026-regular",
  },
];

type ParameterSelectorsProps = {
  position: string;
  setPosition: Dispatch<SetStateAction<string>>;
  week: string;
  setWeek: Dispatch<SetStateAction<string>>;
  season: string;
  setSeason: Dispatch<SetStateAction<string>>;
};

export function ParameterSelectors({
  position,
  setPosition,
  week,
  setWeek,
  season,
  setSeason,
}: ParameterSelectorsProps) {
  return (
    <div className="flex flex-col gap-2 border-t border-b py-3 border-white w-72">
      <div className="flex gap-1 items-center">
        <p>Show me the top 10</p>
        <Select
          items={POSITIONS}
          value={position}
          onValueChange={(newValue) =>
            setPosition(newValue ?? POSITIONS[0].value)
          }
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              {POSITIONS.map((position) => (
                <SelectItem key={position.value} value={position.value}>
                  {position.label}
                </SelectItem>
              ))}
            </SelectGroup>
          </SelectContent>
        </Select>
        <p>prospects</p>
      </div>
      <div className="flex gap-1 items-center">
        <p>In week</p>
        <Select
          items={WEEKS}
          value={week}
          onValueChange={(newValue) => setWeek(newValue ?? WEEKS[0].value)}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              {WEEKS.map((week) => (
                <SelectItem key={week.value} value={week.value}>
                  {week.label}
                </SelectItem>
              ))}
            </SelectGroup>
          </SelectContent>
        </Select>
      </div>
      <div className="flex gap-1 items-center">
        <p>Of the</p>
        <Select
          items={SEASONS}
          value={season}
          onValueChange={(newValue) => setSeason(newValue ?? SEASONS[0].value)}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              {SEASONS.map((season) => (
                <SelectItem key={season.value} value={season.value}>
                  {season.label}
                </SelectItem>
              ))}
            </SelectGroup>
          </SelectContent>
        </Select>
        <p>NFL season</p>
      </div>
    </div>
  );
}
