import re
import itertools
import random


class AIPlayer:
    """
    This encapsulates a rational-thinking AI opponent.

    In order to understand what the opponent is thinking, please wach this video:

    http://www.youtube.com/watch?v=o3Z3oAoKhDA

    or read this article:

    http://en.wikipedia.org/wiki/Minimax#Minimax_algorithm_with_alternate_moves

    The AI player is attempting to *maximize* terminal score, and understands that the human
    attempts to *minimize* terminal score.

    The only class-level variable here is a dictionary where we save off the scores of
    individual situations.  This is class-level because the information contained within
    is always true.  
    """
    #scores of various board positions
    score_dict={}

    def score_move(self,board,(move,player)):
        """
        if "player" committed "move", what would the score of the
        resulting board be?
        """
        result_board=board.commit_move(move,player)
        return self.score_posn(result_board, PlayerTypes.opposing_player(player))

    def best_next_move(self,board,player):
        """
        This is used for the A-I part of the game.  It looks for a move whose
        resulting board will have an optimal score.  
        TODO: pick randomly among optimal moves, to give game some human feel.
        """
        cur_posn_score=self.score_posn(board,player)
        for m in board.remaining_moves():
            if self.score_move(board,(m,player))==cur_posn_score:
                return m
    
    def record_score(self,board,player,score):
        """
        this is just a wrapper to make the code read more like english
        and to handle assertion-checking
        """
        #extract the hashable property of the board object
        board_tuple=board.board
        if (board_tuple,player) in self.score_dict:
            assert self.score_dict[(board_tuple,player)]==score
        else:
            self.score_dict[(board_tuple,player)]=score

    def score_posn(self,board,player):
        """
        What is the "score" of the current board?
        see above for an explanation of what "score" means
        Note that we are using a dictionary object to avoid extra work
        """
        cur_winner=board.winner_on_board()
        if cur_winner!=0:
            #first obvious check - is the game over?
            self.record_score(board,player,cur_winner)
            return cur_winner
        elif len(board.remaining_moves())==0:
            #nobody can move, and there is no winner.  stale mate.
            return 0
        elif len(board.remaining_moves()) >=((TicTacToeBoard.board_len*TicTacToeBoard.board_len)-1):
            #you can't lose after two moves.....
            return 0
        elif (board.board,player) in self.score_dict:
            #we've already memorized this into the score dictionary!
            return self.score_dict[(board.board,player)]
        else:
            #all of the obvious checks have yielded no results.
            #so, find the next move yielding maximal (or minimal) score
            cur_remaining_moves=board.remaining_moves()
    
            #suppose we are the score-minimizing player.
            #we want to figure out how small we can make
            #the score of the resulting move
            if player==PlayerTypes.AI:
                 rtn_score=self.find_maximal_score((self.score_move(board,(move,player)) for move in cur_remaining_moves))
            else:
                 rtn_score=self.find_minimal_score((self.score_move(board,(move,player)) for move in cur_remaining_moves))
            self.record_score(board,player,rtn_score)
            return rtn_score

    def find_maximal_score(self,scores):
        rtnval = -1
        for score in scores:
            if score==1:
                rtnval = 1 
                break
            else:
                rtnval=max(rtnval,score)
        return rtnval

    def find_minimal_score(self,scores):
        rtnval = 1
        for score in scores:
            if score==-1:
                rtnval = -1
                break
            else:
                rtnval=min(rtnval,score)
        return rtnval

class PlayerTypes:
    """
    This is analogous to an "enum" from .NET world.
    This allows us to interpret the meanings of the integers
    within the TicTacToeBoard.
    """
    HUMAN=-1
    AI=1
    BLANK=0
    #def __init__(self,contents=BLANK):
        #self.contents=contents
    @staticmethod
    def opposing_player(p):
        assert p != 0
        return p*-1
    @staticmethod
    def player_to_avatar(n):
        if n==-1:
            return "X"
        elif n==0:
            return "_"
        elif n==1:
            return "O"
        else:
            raise ValueError("The board contains numbers outside {-1,0,1}")


class TicTacToeBoard:
    """
    This models a snapshot of a tic tac toe board.  The indended use is for the
    consumer to build a new board every time a move is made.  
    
    Consequently, the only object-level variable is a 2-D tuple, whose elements
    correspond to the pieces on the board.  This tuple is full of integers, whose
    meanings are interpreted via the PlayerTypes class.
    """
    board_len=3
    
    
    def __init__(self,board=None):
        """
        Provide a board where 0 indicates an empty slot, and 1 and -1 indicate
        pieces on the board.  1 and -1 do not have any special meanings beyond
        what they are used for in "player_to_avatar()", where they inform how the board is printed.
        """
        board=board if board != None else self.default_board()
        self.board=board

    def default_board(self):
        default_row=tuple([0]*self.board_len)
        return tuple([default_row]*self.board_len)

    def remaining_moves(self):
        """
        what squares haven't filled up yet?
        """
        return [(y,x) for (y,x) in itertools.product(range(self.board_len),range(self.board_len)) if self.board[y][x]==PlayerTypes.BLANK]

    def fails_boundaries(self,(input_row,input_col)):
        rtnval=False
        legal_idx_range=set(range(0,self.board_len))
        coordinates_within_bounds=input_row in legal_idx_range and input_col in legal_idx_range
        return not coordinates_within_bounds
    
    def commit_move(self,(move_y,move_x),player):
        """
        Return a fresh board, which looks like the previous board after
        "player" has applied "(move_y,move_x)"
        this is kind of ugly.  i'm not sure how to avoid casting to a list of lists..
        """
        assert (move_y,move_x) in self.remaining_moves(), "committing move to occupied square"
        board_as_list=map(lambda row:list(row),self.board)
        board_as_list[move_y][move_x]=player
        new_board=tuple(map(lambda row:tuple(row),board_as_list))
        return TicTacToeBoard(new_board)
    def grid_path_generator(self,y_step,x_step,starting_posn):
        """
        produces a generator which yields a sequence of positions on the board.
        this is useful for determining whether there is a winner on the board.
        if you want to check for a winner in the first row, you can "walk down" the first row
        making sure that every resident of that row is identical
        """
        cur_posn=starting_posn
        while not self.fails_boundaries(cur_posn):
            yield cur_posn
            cur_posn=(cur_posn[0]+y_step,cur_posn[1]+x_step)

    def winner_on_path(self,path):
        """
        walk along the provided path, seeing if a winning-triplet
        lives on this path.  we require that all three numbers are
        equal and nonzero.
        """
        values_on_path=[self.board[y][x] for (y,x) in path]
        if all([v==PlayerTypes.AI for v in values_on_path]):
            return PlayerTypes.AI
        elif all([v==PlayerTypes.HUMAN for v in values_on_path]):
            return PlayerTypes.HUMAN
        else:
            return PlayerTypes.BLANK

    
    def winner_on_board(self):
        """
        does the current board contain a winner (should this game end)?
        generate all of the possible win-paths, and walk down each one,
        checking for a winner
        """
        col_paths=[self.grid_path_generator(1,0,(0,x)) for x in range(self.board_len)]
        row_paths=[self.grid_path_generator(0,1,(y,0)) for y in range(self.board_len)]
        diagonal_paths=[self.grid_path_generator(1,1,(0,0)),self.grid_path_generator(-1,1,(self.board_len-1,0))]
        winner=0
        for p in col_paths+row_paths+diagonal_paths:
            p_winner=self.winner_on_path(p)
            if p_winner!=0:
                winner=p_winner
                break
        return winner

    def is_occupied_square(self,(input_row,input_col)):
        return (self.board[input_row][input_col]!=0)

    def __str__(self):
        rtn_str="\n".join(["|"+"|".join([PlayerTypes.player_to_avatar(n) for n in row])+"|" for row in self.board])
        return rtn_str
          
def run_tests():
    test_board_0=TicTacToeBoard((( 1, 0, 0),
                                 ( 0, 1, 0),
                                 ( 0, 0, 1)))
    test_board_1=TicTacToeBoard((( 1, 1, 1),
                                 ( 0,-1, 0),
                                 (-1, 0, 0)))
    test_board_2=TicTacToeBoard((( 0,-1, 0),
                                 ( 0,-1, 0),
                                 ( 0,-1, 0)))
    test_board_3=TicTacToeBoard((( 0, 1, 0),
                                 ( 0, 0, 0),
                                 ( 0,-1, 0)))
    test_board_4=TicTacToeBoard(((-1,-1, 1),
                                 ( 1, 0, 0),
                                 (-1, 1, 0)))
    test_board_5=TicTacToeBoard(((-1,-1, 1),
                                 ( 1, 1, 0),
                                 (-1,-1, 1)))
    test_board_6=TicTacToeBoard((( 0, 0, 0),
                                 ( 0, 0, 0),
                                 ( 0,-1, 0)))
    test_board_6=TicTacToeBoard((( 1, 0, 0),
                                 ( 0, 0, 0),
                                 ( 0, 0,-1)))
    ai_player=AIPlayer()
    assert (test_board_6.winner_on_board() == 0)
    assert (test_board_1.winner_on_board() == 1)
    assert (ai_player.best_next_move(test_board_4,1) == (1,2))
    assert (ai_player.best_next_move(test_board_4,-1) == (1,1))
    assert (ai_player.score_posn(test_board_6,1) == 1)
    assert (ai_player.score_posn(test_board_6,-1) == -1)


if __name__=="__main__":
    run_tests()
