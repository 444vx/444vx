# Proste Kółko i Krzyżyk w terminalu

def print_board(board):
    print("\n")
    for i in range(3):
        print(" | ".join(board[i]))
        if i < 2:
            print("--+---+--")
    print("\n")

def check_win(board, player):
    # Sprawdzanie wierszy, kolumn i przekątnych
    for i in range(3):
        if all(board[i][j] == player for j in range(3)):
            return True
        if all(board[j][i] == player for j in range(3)):
            return True
    if board[0][0] == board[1][1] == board[2][2] == player:
        return True
    if board[0][2] == board[1][1] == board[2][0] == player:
        return True
    return False

def main():
    board = [[" "]*3 for _ in range(3)]
    players = ["X", "O"]
    turn = 0

    while True:
        print_board(board)
        player = players[turn % 2]
        move = input(f"Ruch gracza {player} (np. 1 1): ")
        try:
            x, y = map(int, move.split())
            if board[x-1][y-1] != " ":
                print("Pole zajęte! Spróbuj jeszcze raz.")
                continue
            board[x-1][y-1] = player
        except:
            print("Niepoprawny ruch! Użyj formatu 'wiersz kolumna', np. 1 1")
            continue

        if check_win(board, player):
            print_board(board)
            print(f"Gratulacje! Gracz {player} wygrał!")
            break

        if all(board[i][j] != " " for i in range(3) for j in range(3)):
            print_board(board)
            print("Remis!")
            break

        turn += 1

if __name__ == "__main__":
    main()
