import { Player } from "@/actions/actions";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "./ui/table";
import { ScrollArea } from "./ui/scroll-area";

type PlayersTableProps = { players: Player[] };

export function PlayersTable({ players }: PlayersTableProps) {
  return (
    <ScrollArea className="h-143.75">
      <Table className="w-96">
        <TableHeader>
          <TableRow>
            <TableHead>Player</TableHead>
            <TableHead>Team</TableHead>
            <TableHead className="text-right">Projected Points</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {players.map((player) => {
            const name = `${player.first_name} ${player.last_name}`;
            return (
              <TableRow key={name}>
                <TableCell className="font-medium">{name}</TableCell>
                <TableCell>{player.team}</TableCell>
                <TableCell className="text-right">
                  {Math.round(player.projected_points * 100) / 100}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </ScrollArea>
  );
}
