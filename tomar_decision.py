import json
import chess
import chess.engine


def load_board_from_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data


def board_to_dict(board_json):
    return {cell['position']: cell['piece'] for cell in board_json if cell['piece']}


def find_move(before_board, after_board):
    before = board_to_dict(before_board)
    after = board_to_dict(after_board)

    moved_from = None
    moved_to = None

    for pos in before:
        if pos not in after:
            moved_from = pos
        elif before[pos] != after[pos]:
            moved_from = pos

    for pos in after:
        if pos not in before:
            moved_to = pos
        elif before.get(pos) != after[pos]:
            moved_to = pos

    return moved_from, moved_to


def json_to_fen(json_board):
    board = [['' for _ in range(8)] for _ in range(8)]
    piece_map = {
        'pawn': 'p', 'knight': 'n', 'bishop': 'b',
        'rook': 'r', 'queen': 'q', 'king': 'k'
    }

    for cell in json_board:
        if cell['piece']:
            piece = cell['piece']
            symbol = piece_map[piece['type'].lower()]
            if piece['color'] == 'white':
                symbol = symbol.upper()
            x = 8 - int(cell['position'][1])
            y = ord(cell['position'][0]) - ord('a')
            board[x][y] = symbol

    fen_rows = []
    for row in board:
        empty = 0
        fen_row = ''
        for square in row:
            if square == '':
                empty += 1
            else:
                if empty:
                    fen_row += str(empty)
                    empty = 0
                fen_row += square
        if empty:
            fen_row += str(empty)
        fen_rows.append(fen_row)
    fen = '/'.join(fen_rows) + ' w KQkq - 0 1'
    return fen


def suggest_move(fen):
    board = chess.Board(fen)
    with chess.engine.SimpleEngine.popen_uci("stockfish") as engine:
        result = engine.play(board, chess.engine.Limit(time=0.1))
    return result.move


def decidir(before_file, after_file):
    before_board = load_board_from_json(before_file)
    after_board = load_board_from_json(after_file)

    moved_from, moved_to = find_move(before_board, after_board)
    print(f"Movimiento detectado: {moved_from} -> {moved_to}")

    fen = json_to_fen(after_board)
    print(f"FEN actual: {fen}")

    best_move = suggest_move(fen)
    print(f"Mejor respuesta sugerida: {best_move}")
