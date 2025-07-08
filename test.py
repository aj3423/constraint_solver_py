from rich import print
from datetime import datetime

from test_alphametics import parse_question

question = "SEND + MORE = MONEY"  # 0.0009 sec(all, one)
# question = "I + BB == ILL"
# question = "AS + A == MOM"
# question = "NO + NO + TOO == LATE"
# question = "HE + SEES + THE == LIGHT"
# question = "A + A + A + A + A + A + A + A + A + A + A + B == BCC"
# question = "AND + A + STRONG + OFFENSE + AS + A + GOOD == DEFENSE"

# slow
# 0.28 sec(all)  0.02 sec(one)
# question = "TEN + HERONS + REST + NEAR + NORTH + SEA + SHORE + AS + TAN + TERNS + SOAR + TO + ENTER + THERE + AS + HERONS + NEST + ON + STONES + AT + SHORE + THREE + STARS + ARE + SEEN + TERN + SNORES + ARE + NEAR == SEVVOTH"
# 0.04 sec(all) 0.01 sec(one)
# question = "SO + MANY + MORE + MEN + SEEM + TO + SAY + THAT + THEY + MAY + SOON + TRY + TO + STAY + AT + HOME +  SO + AS + TO + SEE + OR + HEAR + THE + SAME + ONE + MAN + TRY + TO + MEET + THE + TEAM + ON + THE + MOON + AS + HE + HAS + AT + THE + OTHER + TEN == TESTS"
# 3 sec(all)  0.6 sec(one)
# question = "THIS + A + FIRE + THEREFORE + FOR + ALL + HISTORIES + I + TELL + A + TALE + THAT + FALSIFIES + ITS + TITLE + TIS + A + LIE + THE + TALE + OF + THE + LAST + FIRE + HORSES + LATE + AFTER + THE + FIRST + FATHERS + FORESEE + THE + HORRORS + THE + LAST + FREE + TROLL + TERRIFIES + THE + HORSES + OF + FIRE + THE + TROLL + RESTS + AT + THE + HOLE + OF + LOSSES + IT + IS + THERE + THAT + SHE + STORES + ROLES + OF + LEATHERS + AFTER + SHE + SATISFIES + HER + HATE + OFF + THOSE + FEARS + A + TASTE + RISES + AS + SHE + HEARS + THE + LEAST + FAR + HORSE + THOSE + FAST + HORSES + THAT + FIRST + HEAR + THE + TROLL + FLEE + OFF + TO + THE + FOREST + THE + HORSES + THAT + ALERTS + RAISE + THE + STARES + OF + THE + OTHERS + AS + THE + TROLL + ASSAILS + AT + THE + TOTAL + SHIFT + HER + TEETH + TEAR + HOOF + OFF + TORSO + AS + THE + LAST + HORSE + FORFEITS + ITS + LIFE + THE + FIRST + FATHERS + HEAR + OF + THE + HORRORS + THEIR + FEARS + THAT + THE + FIRES + FOR + THEIR + FEASTS + ARREST + AS + THE + FIRST + FATHERS + RESETTLE + THE + LAST + OF + THE + FIRE + HORSES + THE + LAST + TROLL + HARASSES + THE + FOREST + HEART + FREE + AT + LAST + OF + THE + LAST + TROLL + ALL + OFFER + THEIR + FIRE + HEAT + TO + THE + ASSISTERS + FAR + OFF + THE + TROLL + FASTS + ITS + LIFE + SHORTER + AS + STARS + RISE + THE + HORSES + REST + SAFE + AFTER + ALL + SHARE + HOT + FISH + AS + THEIR + AFFILIATES + TAILOR + A + ROOFS + FOR + THEIR + SAFE == FORTRESSES"

#   impossible
# question = "A == B"
# question = "ACA + DD == BD"

solver = parse_question(question)
# solver.find_all = True
solver.print()

st = datetime.now()
solver.solve()
et = datetime.now()

print("time cost:", et - st)
print("All solutions:")

for s in solver.solutions:
    print(s)
