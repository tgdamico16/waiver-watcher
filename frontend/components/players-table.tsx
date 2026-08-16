import { Player } from "@/actions/actions";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "./ui/table";

type PlayersTableProps = { players: Player[] };

export function PlayersTable({ players }: PlayersTableProps) {
  return (
    <Table className="w-96">
      <TableHeader>
        <TableRow>
          <TableHead>Player</TableHead>
          <TableHead>Team</TableHead>
          <TableHead className="text-right">Projected Points</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {players.map((player) => (
          <TableRow key={player.id}>
            <TableCell className="font-medium">
              {player.first_name} {player.last_name}
            </TableCell>
            <TableCell>{player.team}</TableCell>
            <TableCell className="text-right">
              {Math.round(player.projected_points * 100) / 100}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
