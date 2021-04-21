#!/usr/bin/env python

from bullet import Bullet, Input, YesNo, VerticalPrompt

cli = Bullet(
        prompt = "Please select: ",
        choices = ["aaa", "bbb", "ccc"],
        indent = 0
      )

ret = cli.launch()
print("you choice: ", ret)

cli2 = VerticalPrompt(
       [
         Input(" Set IP addr:")
       ]
       )

ret = cli2.launch()
print("IP: ", ret[0][1])
