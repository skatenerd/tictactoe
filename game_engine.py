from tic_tac_toe_utils import *


def parse_to_integer_pair(input_str):
    """
    Trying to be flexible.  Try to extract two natural numbers from
    the input.
    """
    num_regex=re.compile(r'[0-9]+')
    matches=num_regex.findall(input_str)
    if len(matches)==2:
        #Easy case.  we found two number-looking things.
        return tuple([int(m) for m in matches])
    elif len(matches)==1 and len(matches[0])==2:
        #harder case.  The user entered something like "12"
        #parse it to (1,2)
        return(int(matches[0])/10,int(matches[0])%10)
    else:
        return None

def prompt_valid_move(board):
    """
    extract meaningful input from user.  keep trying until something
    useful comes out
    """
    move=parse_to_integer_pair(raw_input("Please enter your move\n"))
    valid_move=False
    while not valid_move:
        if not move:
            move=parse_to_integer_pair(raw_input("I cannot parse your move into coordinates, try again\n"))
        elif board.fails_boundaries(move):
            move=parse_to_integer_pair(raw_input("Previous move was off the board, try again\n"))
        elif board.is_occupied_square(move):
            move=parse_to_integer_pair(raw_input("Prevoius move was in an occupied place, try again\n"))
        else:
            valid_move=True
    return move



def run_game():
    print "\n\n\nwelcome.  you will enter your moves in ZERO-INDEXED ROW,COLUMN format."
    print "so, (0,0) is a valid move.  (2,0) means the lower left corner"
    print "this is NOT the same as the x,y coordinates of your childhood\n\n"
    cur_board=TicTacToeBoard()
    ai_player=AIPlayer()
    cur_player=1

    #Pick randomly whether the human player will go first.  If the player goes first
    #the player will play as "O" and try to maximize score.  If player goes second,
    #the player will play as "X" and try to minimize score.
    cur_player = 1 if random.random() > .5 else -1
    print ("we have chosen randomly for you."+
          "you will move {0} and play as {1}.".format("first" if PlayerTypes.HUMAN==cur_player else "second",
                                                      "\""+str(PlayerTypes.player_to_avatar(PlayerTypes.HUMAN)+"\"")))
    while not cur_board.winner_on_board() and len(cur_board.remaining_moves())>0:
        #main game loop....
        if cur_player==PlayerTypes.HUMAN:
            move=prompt_valid_move(cur_board)
        else:
            move=ai_player.best_next_move(cur_board,cur_player)
            print "computer has chosen {0}".format(move)
        cur_board=cur_board.commit_move(move,cur_player)
        print cur_board
        print "\n"
        cur_player=PlayerTypes.other_player(cur_player)                                                                                       

    if cur_board.winner_on_board()==PlayerTypes.AI:
        print "i win!"
    else:
        print "we tied.  you must be brilliant"

if __name__=="__main__":
    run_game()
