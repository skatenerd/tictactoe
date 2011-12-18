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

def str_to_bool(inp_to_parse,yes_responses,no_responses):
    if inp_to_parse in yes_responses:
        return True
    elif inp_to_parse in no_responses:
        return False
    else:
        raise Exception("Input not parseable to bool")

def prompt_first_player():
    yes_responses=set(("yes","true","1","y","t",""))
    no_responses=set(("no", "n", "0", "false"))
    valid_responses=yes_responses.union(no_responses)
    current_input_attempt=raw_input("Would you like to go first? [default yes]\n")
    while (current_input_attempt not in valid_responses):
        current_input_attempt=raw_input("Could not parse previous response.  Try again\n")
    human_first=str_to_bool(current_input_attempt,yes_responses,no_responses)
    if human_first:
        return PlayerTypes.HUMAN
    else:
        return PlayerTypes.AI



def run_game(starting_player):
    cur_board=TicTacToeBoard()
    ai_player=AIPlayer()
    cur_player=starting_player
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
        cur_player=PlayerTypes.opposing_player(cur_player)                                                                                       
    return cur_board.winner_on_board()


if __name__=="__main__":
    print "\n\n\nwelcome.  you will enter your moves in ZERO-INDEXED ROW,COLUMN format."
    print "so, (0,0) is a valid move.  (2,0) means the lower left corner"
    print "this is NOT the same as the x,y coordinates of your childhood\n\n"
    cur_player=prompt_first_player()

    #Pick randomly whether the human player will go first.  If the player goes first
    #the player will play as "O" and try to maximize score.  If player goes second,
    #the player will play as "X" and try to minimize score.
    print ("You have elected to move move {0} and play as {1}.".format(
        "first" if PlayerTypes.HUMAN==cur_player else "second",
        "\""+str(PlayerTypes.player_to_avatar(PlayerTypes.HUMAN)+"\"")))
    outcome=run_game(cur_player)
    if outcome==PlayerTypes.AI:
        print "i win!"
    else:
        print "we tied.  you must be brilliant"
    

