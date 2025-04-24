## SnapshotPointLine

1. lines[:][0] == range(1, lines.size + 1, 1)
2. if (lines[n][2] == null) -> typeof lines[n+1][1] == snapshot
3. if (lines[n][2] == null) -> lines[n].size == 5 else 8
4. lines[:][6] == lines[:][7] == null
5. lines[0][3] == lines[-1][3] == 1, lines[1:-1][3] == null
6. lines[:][4] might be the line number of the original `.ks` file. lines[0][4] >= scn.scene.firstLine
7. lines[:][2] maps to indexes of scn.texts. lines[:][5] == texts[:][3]
